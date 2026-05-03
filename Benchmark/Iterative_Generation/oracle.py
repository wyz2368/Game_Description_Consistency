from llm import call_llm
from collections import defaultdict, Counter
from utils import get_path_to_node
import re
import ast
import os


def get_action_label_path_to_node(node):
    path = []
    while node.parent:
        path.append(node.prior_action.label)
        node = node.parent
    path.reverse()
    return path


def action_label_path_to_python_expr(action_label_path):
    expr = "g.root"
    for action_label in action_label_path:
        expr += f".children[{repr(action_label)}]"
    return expr


def append_to_oracle_log(log_path: str, title: str, content: str) -> None:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"{title}\n")
        f.write(f"{'=' * 80}\n")
        f.write(content if content.strip() else "[EMPTY]")
        if not content.endswith("\n"):
            f.write("\n")


def generate_info_set_label(
    path_to_node,
    game_description,
    player,
    prev_labels,
    player_actions_dict,
    model: str = "gpt-5-mini",
    temperature: float = 0.0,
    log_path: str = None,
):
    """
    Calls the LLM to produce an infoset label payload.

    Expected LLM output: a Python code block containing ONE dict with keys:
      - "label": int (or digit-string)
      - "one_sentence_description": str
    """

    print("\n\nGenerating info set label for player", player)
    print("Player:", player)
    print(f"Path to node: {path_to_node}")
    print("Previous labels:", prev_labels)

    prompt = f"""
    You are an expert in game theory.

    Key definitions:
        - A node corresponds to a HISTORY: a sequence of actions (including chance actions).
        - An information set (infoset) is a COLLECTION OF NODES, i.e., a SET OF HISTORIES.
        - A player's "observation" at an infoset is nothing more or less than: ONE of the histories in that infoset happened, but the player does not know which one.
        - An information set can be represented by a label that describes the corresponding set of histories. For example, in a poker game, a label may describe all histories in the following way: the player holds a fixed private hand and has observed the same sequence of public actions, while the opponents' private cards are unobserved.
        - However, there exist game descriptions witout a succinct description of the information structure when information sets are described essentially by an explicit enumeration of the histories of nodes in the set. In this case, our node label will have to explicitly enumerate all such histories.

    Your task:
    Determine whether the current decision node of Player {player} belongs to one of Player {player}'s previously labeled information sets.
    - If yes, reuse that label.
    - If no, create a new label and a one-sentence description of the current information set.

    Inputs:
    - Player Actions Dictionary:
    {player_actions_dict}

    - Game Description:
    {game_description}

    - Current Node History:
    {path_to_node}
    If the history is empty, the node is the root.

    - Previous Labels for Player {player}:
    {prev_labels}

    Instructions:

    Step 1: Locate the current node
    Identify where the current node lies in the game tree from the given history. If the node has empty history, it is the root.

    Step 2: Analyze Player {player}'s information along the path
    For each such decision point, determine:
        1. What action Player {player} took there, if any.
        2. Between that decision point and the next decision point of Player {player} (or from the root to the first one):
           - which actions of other players or chance Player {player} can distinguish,
           - which actions of other players or chance Player {player} cannot distinguish.
        3. What Player {player} remembers at the current node:
           - whether Player {player} remembers their own past actions,
           - whether Player {player} remembers earlier observations,
           - whether any previously known information has been forgotten.
    Do NOT analyze observations that are not present in the current history.
    External or unnecessary information does not affect the information set.

    Step 3: Duplicate check
        Examine each previous label for Player {player}, one at a time.
        For each label, determine whether the current node history belongs to the infoset already described by that label. 
        If the current node belongs to one of those previously labeled infosets, reuse that label.
        Otherwise, create a new label as described in step 4.

    Step 4: If no previous label matches, create a new infoset label
        1) Write a one-sentence description of Player {player}'s current information set as the label.
           The description MUST be broad enough to describe exactly the set of histories (nodes) that Player {player} cannot distinguish between at this point.
           Describe Player {player}'s remembered information sequentially from the first action that appears in the history to the current node, based on the analysis above.

           If an action or chance outcome is not fully observed, write down that uncertainty only when it is necessary to describe the current information set exactly.
           However, if an action is observed by Player {player}, just write that Player {player} observed that action at that stage.

           Do NOT include the general observation rule in the description.
           For example, suppose the history is:
           A:a1, B:b1, A:b2
           and at B's first decision node, B can observe a1 but cannot distinguish a2 from a3.
           Then the description should say that B observed a1 at the first stage.
           It should NOT also say that B cannot distinguish a2 from a3 at that first stage, because that is part of the general observation rule rather than part of the specific remembered history that should be recorded in the label.

           Do NOT include observations that are not in the history.
           For example, if the history is:
              Chance: object 2 -> Player: Choose object 3
           and Player observes that object 1 is revealed, then the sentence may only refer to whether Player observes object 2 and that Player previously chose object 3.
           Do not add information that is absent from the history.
           
           If some earlier information is no longer remembered by Player {player} at the current node, do NOT include it in the description.

           If the information set can be described simply and exactly, use such a description.
           If it cannot be described simply and exactly, explicitly enumerate the histories (nodes) in the information set.

        2) Assign the next available numeric label (or 1 if none exist).

    ## Output format
    Before producing the final answer, explain your reasoning.

    After all reasoning, return a Python code block containing exactly one dict with keys:
    ```python
    {{
        "label": numeric number,
        "one_sentence_description": str,
    }}
    ```
    """

    max_retries = 3
    last_err = None

    for attempt in range(1, max_retries + 1):
        try:
            raw = call_llm(
                prompt,
                model=model,
                temperature=temperature,
            )

            print(f"LLM response: {raw}")

            if log_path:
                append_to_oracle_log(
                    log_path,
                    f"LLM RESPONSE | attempt={attempt} | player={player} | node={path_to_node}",
                    raw,
                )

            match = re.search(r"```python\s*(.+?)\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
            if not match:
                raise ValueError("No ```python ... ``` code block found in LLM output.")

            code_str = match.group(1).strip()

            try:
                obj = ast.literal_eval(code_str)
            except Exception as e:
                raise ValueError(f"Could not parse LLM response as Python dict: {e}\nCode was:\n{code_str}")

            if not isinstance(obj, dict):
                raise ValueError(f"LLM output is not a dict: {type(obj)}")

            required = {"label", "one_sentence_description"}
            missing = required - set(obj.keys())
            extra = set(obj.keys()) - required

            if missing:
                raise ValueError(f"Missing keys in LLM dict: {missing}. Got keys: {list(obj.keys())}")
            if extra:
                raise ValueError(f"Extra keys in LLM dict (not allowed): {extra}")

            label = obj["label"]
            one_sentence_description = obj["one_sentence_description"]

            if not isinstance(label, int):
                if isinstance(label, str) and label.strip().isdigit():
                    label = int(label.strip())
                else:
                    raise ValueError(f"label must be int (or digit-string). Got: {label} ({type(label)})")

            if not isinstance(one_sentence_description, str):
                raise ValueError("one_sentence_description must be str.")

            if log_path:
                append_to_oracle_log(
                    log_path,
                    f"PARSED RESULT | player={player} | node={path_to_node}",
                    str({
                        "label": label,
                        "one_sentence_description": one_sentence_description,
                    }),
                )

            return label, one_sentence_description

        except Exception as e:
            last_err = e
            print(f"Attempt failed: {e}")
            print("Retrying...\n")

            if log_path:
                append_to_oracle_log(
                    log_path,
                    f"ERROR | attempt={attempt} | player={player} | node={path_to_node}",
                    str(e),
                )

    raise RuntimeError(f"Failed to generate info set label after multiple attempts. Last error: {last_err}")


def assign_information_sets_with_labels(
    g,
    game_description,
    player_actions_dict,
    model: str = "gpt-5-mini",
    temperature: float = 0.0,
    log_dir: str = None,
):
    """
    Assign infosets using LLM-generated labels.
    """
    player_label_rep = defaultdict(dict)      # player -> {label: representative_node}
    player_label_payload = defaultdict(dict)  # player -> {label: payload}

    replay_path = None
    log_path = None
    if log_dir is not None:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "oracle_log.txt")
        replay_path = os.path.join(log_dir, "replay_infosets.py")

        with open(log_path, "w", encoding="utf-8") as f:
            f.write("Oracle log\n")

        with open(replay_path, "w", encoding="utf-8") as f:
            f.write("def replay_infosets(g):\n")
            f.write('    """Replays g.set_infoset(...) calls."""\n')

    def dfs(node):
        if node.player != g.players.chance and not node.is_terminal:
            player = node.player.label
            path_to_node = get_path_to_node(g, node)

            prev_labels = [
                {
                    "label": lbl,
                    "one_sentence_description": payload["one_sentence_description"],
                }
                for lbl, payload in player_label_payload[player].items()
            ]

            label, one_sentence_description = generate_info_set_label(
                path_to_node=path_to_node,
                game_description=game_description,
                player=player,
                prev_labels=prev_labels,
                player_actions_dict=player_actions_dict,
                model=model,
                temperature=temperature,
                log_path=log_path,
            )

            if label in player_label_rep[player]:
                rep_node = player_label_rep[player][label]
                g.set_infoset(node, rep_node.infoset)

                if replay_path:
                    node_action_path = get_action_label_path_to_node(node)
                    rep_action_path = get_action_label_path_to_node(rep_node)

                    node_expr = action_label_path_to_python_expr(node_action_path)
                    rep_expr = action_label_path_to_python_expr(rep_action_path)

                    with open(replay_path, "a", encoding="utf-8") as f:
                        f.write(f"    g.set_infoset({node_expr}, {rep_expr}.infoset)\n")

                if log_path:
                    append_to_oracle_log(
                        log_path,
                        f"INFOSET REUSE | player={player} | node={path_to_node}",
                        f"Reused label {label}",
                    )
            else:
                player_label_rep[player][label] = node
                if log_path:
                    append_to_oracle_log(
                        log_path,
                        f"INFOSET NEW | player={player} | node={path_to_node}",
                        f"Created label {label}",
                    )

            player_label_payload[player][label] = {
                "one_sentence_description": one_sentence_description,
            }

        for child in node.children:
            dfs(child)

    dfs(g.root)

    if log_path:
        append_to_oracle_log(log_path, "FINAL PAYLOAD", str(dict(player_label_payload)))

    return player_label_payload