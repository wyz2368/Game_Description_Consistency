from typing import Dict, Union, List, Tuple
from .chatbot import infer_response
from .utils import safe_extract_player_list

from Tree import NodeType
import re

Key = Union[int, str]  # player number or "chance"

def parse_reason_answer_block(response: str) -> Tuple[str, str]:
    """
    Parse:
      <reason>...</reason>
      <answer>True|False</answer>
    """
    reason_match = re.search(r"<reason>\s*(.*?)\s*</reason>", response, re.DOTALL)
    answer_match = re.search(r"<answer>\s*(True|False)\s*</answer>", response, re.DOTALL)

    if not answer_match:
        raise ValueError(f"Invalid check response format: {response}")

    reason = reason_match.group(1).strip() if reason_match else ""
    answer = answer_match.group(1).strip()
    return reason, answer

def check_name_consistent(
    original_actions: List[str],
    ref_actions: List[str],
    model: str,
    game_description: str,
) -> Tuple[str, str]:
    """
    Returns:
        (answer, reason)
    where answer is "True" or "False"
    """
    prompt_check_valid = (
        f"You are given a game description and two lists of action labels.\n\n"
        f"Game description:\n{game_description}\n\n"
        f"Generated Actions: {original_actions}\n"
        f"Reference Actions: {ref_actions}\n\n"
        f"Decide whether these two lists refer to the same set of underlying game actions.\n"
        f"Focus on the underlying game choice, not surface wording.\n"
        f"Treat different naming conventions as equivalent when they refer to the same action.\n"
        f"Use the game description to resolve coordinates, positions, shorthand, aliases, or paraphrases.\n\n"
        f"Focus only on whether the labels match. Do not consider whether it is a chance node action or a player action.\n"
        f"Examples:\n"
        f"- ['C', 'S'] and ['Signal C', 'Signal S'] should be treated as the same if C and S are the relevant underlying alternatives.\n"
        f"- ['Left', 'Right'] and ['L', 'R'] should be treated as the same.\n\n"
        f"It is okay for a chance outcome, signal, or state to use labels that look like player actions, and vice versa.\n"
        f"For example, ['Fire'] and ['Loaded'] are equivalent when both denote the same underlying outcome in the game, even though one sounds like an action and the other like a state.\n"
        f"Do not reject a match merely because one label is phrased as an action and the other as a state, outcome, or signal.\n"
        f"When a label specifies a mark such as X or O but the game description makes clear whose turn it is, treat labels like 'Place X at ...', 'Place O at ...', and neutral labels like 'Place at ...' as equivalent if they refer to placing the current player's mark at the same coordinates.\n"
        f"Output format:\n"
        f"<reason>\n"
        f"Provide a brief explanation in 2 to 4 sentences.\n"
        f"Explain how the generated actions correspond to the reference actions.\n"
        f"</reason>\n"
        f"<answer>\n"
        f"True or False\n"
        f"</answer>\n\n"
        f"Do not output anything outside these tags."
    )

    response = infer_response(prompt_check_valid, model)
    print("Raw check response:", response)

    reason, answer = parse_reason_answer_block(response)

    print("Check reason:", reason)
    print("Check final answer:", answer)

    return answer, reason


def match_all_actions_llm(
    original_actions: List[str],
    ref_actions: List[str],
    model: str,
    game_description: str,
) -> Dict[str, str]:
    """
    Returns a mapping {generated_action_name -> reference_action_name}.
    The LLM must return the mapped list in the SAME ORDER as original_actions.
    """
    if not original_actions:
        raise ValueError("Empty original_actions provided.")

    print("Original actions:", original_actions)
    print("Reference actions:", ref_actions)

    check_result, reason = check_name_consistent(
        original_actions=original_actions,
        ref_actions=ref_actions,
        model=model,
        game_description=game_description,
    )

    if check_result != "True":
        raise ValueError(
            "The actions in the generated game do not match the actions in the reference game. "
            f"Reason: {reason}"
        )

    prompt = (
        f"You are given a game description and two lists of action labels that refer to the same set of game actions.\n\n"
        f"Game description:\n{game_description}\n\n"
        f"Generated Actions: {original_actions}\n"
        f"Reference Actions: {ref_actions}\n\n"
        f"Task: replace each generated action with the best-matching reference action.\n\n"
        f"Match actions by their underlying meaning in the game, not by surface wording.\n"
        f"Use the game description to resolve paraphrases, alternate naming conventions, coordinates, shorthand, or role-specific wording.\n"
        f"Keep the exact same order as the generated actions list.\n"
        f"Do not add, remove, or reorder items.\n"
        f"Each output item must be chosen from the reference actions list.\n\n"
        f"Return ONLY the mapped list in valid Python list format."
    )

    response = infer_response(prompt, model)
    print("Raw mapping response:", response)

    modified_actions = safe_extract_player_list(response)

    if len(modified_actions) != len(original_actions):
        raise ValueError(
            f"LLM output length mismatch. original={len(original_actions)} modified={len(modified_actions)}"
        )

    # Validate mapped list is the same action set as reference
    if sorted(modified_actions) != sorted(ref_actions):
        raise ValueError(
            f"Mapped actions do not match reference actions.\n"
            f"Modified: {modified_actions}\n"
            f"Reference: {ref_actions}"
        )

    print("Modified actions:", modified_actions)

    return dict(zip(original_actions, modified_actions))

def update_current_nodes(node, modified_actions, ref_actions):

    if node.node_type == NodeType.PLAYER:
        node.actions = ref_actions
        old_children = list(node.children.values())
        
        children_lookup_table = dict(zip(modified_actions, old_children))
        
        new_children = {
            action: children_lookup_table[action] 
            for action in ref_actions
        }
        
        node.children = new_children
    
    elif node.node_type == NodeType.CHANCE:
        node.actions = ref_actions
        new_children = {}
        old_children = list(node.children.values())
        old_probs = node.probs
        new_probs = {}
        
        children_lookup_table = {
            modified_action: (child, prob)
            for modified_action, child, (original_action, prob) in zip(modified_actions, old_children, old_probs.items())
        }

        for action in ref_actions:
            child, prob = children_lookup_table[action]
            new_children[action] = child
            new_probs[action] = prob

        node.children = new_children
        node.probs = new_probs


def build_global_action_mappings(
    ref_total: Dict[Key, List[str]],
    gen_total: Dict[Key, List[str]],
    model: str,
    game_description: str,
) -> Dict[Key, Dict[str, str]]:
    """
    Returns:
      {
        1: {"GenNameA": "RefNameA", ...},
        2: {...},
        "chance": {...}
      }
    """
    mappings: Dict[Key, Dict[str, str]] = {}

    for k, ref_actions in ref_total.items():
        if k not in gen_total:
            raise ValueError(f"Key {k} (player/chance) missing in generated totals.")

        gen_actions = gen_total[k]

        print(f"\nBuilding mapping for key={k}")

        mappings[k] = match_all_actions_llm(
            original_actions=gen_actions,
            ref_actions=ref_actions,
            model=model,
            game_description=game_description,
        )

    return mappings