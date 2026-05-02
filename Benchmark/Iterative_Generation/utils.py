import ast
import re
from collections import defaultdict
from typing import Dict, List
from llm import call_llm
import glob
import os
import pygambit as gbt


def load_efg_from_dir(run_dir: str):
    efg_files = sorted(glob.glob(os.path.join(run_dir, "*.efg")))
    if not efg_files:
        raise FileNotFoundError(f"No .efg file found in {run_dir}")

    if len(efg_files) > 1:
        print(f"Multiple .efg files found in {run_dir}, using: {efg_files[0]}")

    efg_path = efg_files[0]
    g = gbt.read_efg(efg_path)
    return g, efg_path

def info_type_classification_prompt(description: str) -> str:
    """
    STRICT prompt: the model must output EXACTLY one code block with:
      ```info_type
      perfect
      ```
    OR
      ```info_type
      imperfect
      ```
    No extra text.
    """
    return f"""You are an expert on game theory.

Task: Decide whether the game below is PERFECT information or IMPERFECT information.

Definitions:
- PERFECT: the acting player always observes the full history (all prior actions and chance outcomes).
- IMPERFECT: any private/hidden info (secret roles/types/cards, hidden chance outcomes) OR any simultaneous/hidden-action move where a player acts without observing others OR partial observability that implies information sets.

OUTPUT FORMAT (STRICT):
Output EXACTLY ONE block and NOTHING else.

If perfect information:
```info_type
perfect
```
If imperfect information:
```info_type
imperfect
```
Game description:
{description}
""".strip()

def parse_info_type(llm_text: str):
    """
    Extract 'perfect' or 'imperfect' from a ```info_type``` block.
    Returns None if not found.
    """
    info_type_re = re.compile(
        r"```info_type\s*(perfect|imperfect)\s*```",
        re.IGNORECASE | re.DOTALL
    )
    m = info_type_re.search(llm_text or "")
    if not m:
        return None
    return m.group(1).lower()

def classify_game_with_llm(description: str, model: str = "gpt-5-mini", temperature: float = 0.0) -> str:

    prompt = info_type_classification_prompt(description)
    response = call_llm(
        [{"role": "user", "content": prompt}],
        model=model,
        temperature=temperature,
    )
    info_type = parse_info_type(response)
    if info_type not in {"perfect", "imperfect"}:
        raise ValueError(f"Invalid info type classification: {info_type}")
    return info_type

def parse_player_list(text: str) -> list:
    """
    Extracts and parses a Python list of strings from LLM output for players.
    """
    match = re.search(r"\[.*\]", text.strip())
    if match:
        try:
            return ast.literal_eval(match.group(0))
        except Exception:
            return []
    return []

def parse_node_response(response: str) -> tuple:
    """
    Parses an LLM response to extract (node_type, player, actions), even if mixed with markdown or narrative text.
    Handles cases like:
    - "Node Type:, Player: Alice, Actions: ['check', 'bet']"
    Returns:
        (str, str, list): node_type, player, actions
    """
    node_type = None
    player = None
    actions = []

    # Preprocess lines: split comma-separated fields onto new lines
    lines = []
    for line in response.strip().splitlines():
        parts = re.split(r'(?<!\w),\s*(?=\w+[:：])', line)  # split only at commas before a "Key:"
        lines.extend(parts)

    # Match "Field: value"
    pattern = re.compile(r'(?i)(node type|player|actions)\s*[:：]\s*(.*)')

    for line in lines:
        clean = line.strip().lstrip("-*•").strip()
        match = pattern.match(clean)

        if not match:
            continue

        key, val = match.groups()
        key = key.lower()
        val = val.strip()

        if key == "node type":
            node_type = val
        elif key == "player":
            player = val
        elif key == "actions":
            if any(word in val.lower() for word in ["if", "or", "when", "depending"]):
                print(f"[WARNING] Skipping ambiguous actions line: {val}")
                continue
            try:
                actions = ast.literal_eval(val)
                if not isinstance(actions, list):
                    actions = []
            except Exception:
                print(f"[WARNING] Could not parse actions list: {val}")
                actions = []

    # Infer node_type if missing
    if not node_type and player:
        node_type = "Player"
        print(f"[INFO] Inferred missing node_type as 'Player' because player is present.")

    return node_type, player, actions


def zip_chance_data(outcomes, probabilities):
    """
    Combines outcomes and probabilities into a single list of tuples.

    Returns:
        List of (outcome, probability)
    """
    return [
        (outcome, prob)
        for outcome, prob in zip(outcomes, probabilities)
    ]

def maybe_fix_trailing_list_bracket(code: str) -> str:
    """
    If code fails to parse due to an unclosed '[' (common when a return-list
    is cut off), append a closing ']' and return the fixed code.
    Only applies when '[' count > ']' count.
    """
    try:
        import ast
        ast.parse(code)
        return code  # already valid
    except SyntaxError as e:
        msg = str(e).lower()
        # Be conservative: fix only when message clearly signals unclosed '['
        if ("was never closed" in msg or "unexpected eof" in msg or "unterminated" in msg) and code.count('[') > code.count(']'):
            return code.rstrip() + "\n]\n"
        raise  # not our specific issue; bubble up


def get_path_to_node(g, node):
    trajectory = ""
    path = []
    while node.parent:
        # Append tuples for readability first
        if node.parent.player == g.players.chance:
            path.append((f"Chance", node.prior_action.label))
        else:   
            path.append((node.parent.player.label, node.prior_action.label))
        node = node.parent
    
    path.reverse()  # So it goes from root to current node

    # Build formatted trajectory string
    for player, action in path:
        trajectory = f"{trajectory} -> {player}: {action}" if trajectory else f"{player}: {action}"
    
    return trajectory

def extract_player_actions_dict(g) -> Dict[str, List[str]]:
    """
    Traverse an extensive-form game tree and collect unique action names
    available to each player, including chance.

    Returns:
        {
            "chance": ["Heads", "Tails"],
            "Player 1": ["A", "B"],
            "Player 2": ["C", "D"],
        }
    """
    player_to_actions = defaultdict(set)

    def dfs(node):
        if node.is_terminal:
            return

        player = node.player

        if player == g.players.chance:
            player_label = "chance"
        else:
            player_label = str(player.label)

        for child in node.children:
            if child.prior_action is not None:
                action_label = str(child.prior_action.label)
                player_to_actions[player_label].add(action_label)

        for child in node.children:
            dfs(child)

    dfs(g.root)

    return {
        player: sorted(actions)
        for player, actions in player_to_actions.items()
    }

def iter_nodes_dfs(node):
    """Depth-first traversal over the tree."""
    yield node
    for child in node.children:
        yield from iter_nodes_dfs(child)


def make_perfect_information(g):
    """
    Convert an extensive-form game to perfect information by ensuring
    every nonterminal node is alone in its information set.
    """
    for node in iter_nodes_dfs(g.root):
        if node.is_terminal:
            continue

        infoset = node.infoset
        if infoset is None:
            continue

        # If this infoset has multiple members, detach this node
        # into its own singleton infoset.
        if len(infoset.members) > 1:
            g.leave_infoset(node)

    return g