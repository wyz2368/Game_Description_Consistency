from typing import Dict, List
from .chatbot import infer_response
from .utils import safe_extract_player_list
from typing import Dict, Union, List

from collections import deque
from Tree import NodeType

def get_current_level_actions_llm(original_actions: List[str], ref_actions: List[str], model: str) -> Dict[str, str]:
    """
    Returns a mapping {generated_action_name -> reference_action_name}.
    This is computed by asking the LLM to output the renamed list in the SAME ORDER as original_actions.
    """

    if not original_actions:
        raise ValueError("Empty original_actions provided.")

    print("Original actions:", original_actions)
    print("Reference actions:", ref_actions)

    prompt_check_valid = (
        f"You are given two lists of actions\\"
        f"Generated Actions: {original_actions}"
        f"Reference Actions: {ref_actions}"
        f"Disregard the different names and orders. Check if they represent the same meaning of actions."
        f"Output ONLY True if they match and False otherwise."
    )

    response_check = infer_response(prompt_check_valid, model)

    if response_check == "False":
        raise ValueError("The actions in the generated game do not match the actions in the reference game.")

    prompt = (
        f"You are given two lists of actions that refer to the same set of actions.\\"
        f"Generated Actions: {original_actions}"
        f"Reference Actions: {ref_actions}"
        f"Please update the names in this generated list of game actions: {original_actions} so that they match the names in the reference list.\n"
        f"Do not change the order of items in the generated list.\n"
        f"Only return the modified list in Python list format."
    )

    response = infer_response(prompt, model)
    modified_actions = safe_extract_player_list(response)

    if len(modified_actions) != len(original_actions):
        raise ValueError(
            f"LLM output length mismatch. original={len(original_actions)} modified={len(modified_actions)}"
        )

    print("Modified actions:", modified_actions)

    # Mapping: generated name -> reference name
    mapping = dict(zip(original_actions, modified_actions))
    return mapping

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

Key = Union[int, str]  # player number or "chance"

def build_global_action_mappings(ref_total: Dict[Key, List[str]],
                                 gen_total: Dict[Key, List[str]],
                                 model: str) -> Dict[Key, Dict[str, str]]:
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

        # LLM produces mapping for this key
        mappings[k] = get_current_level_actions_llm(gen_actions, ref_actions, model)

    return mappings

def traverse_and_update(ref_root, gen_root, mappings):
    """
    Traverse both trees together.
    For each PLAYER/CHANCE node in generated tree, rename its actions using the key-specific mapping,
    then call update_current_nodes(gen_node, modified_actions, ref_actions_from_ref_node).
    """
    q_ref = deque([ref_root])
    q_gen = deque([gen_root])

    while q_ref and q_gen:
        r_node = q_ref.popleft()
        g_node = q_gen.popleft()

        # Basic structural checks
        if r_node.node_type != g_node.node_type:
            raise ValueError(f"Node type mismatch: ref={r_node.node_type} gen={g_node.node_type}")

        if g_node.node_type in (NodeType.PLAYER, NodeType.CHANCE):
            if not r_node.actions or not g_node.actions:
                raise ValueError("Missing actions on non-terminal node.")

            # Pick mapping key
            if g_node.node_type == NodeType.CHANCE:
                key = "chance"
            else:
                key = g_node.player  # player-by-player mapping

            if key not in mappings:
                raise ValueError(f"No mapping found for key={key}")

            key_map = mappings[key]

            # Rename generated actions in its OWN order
            modified_actions = []
            for a in g_node.actions:
                if a not in key_map:
                    raise ValueError(f"Generated action '{a}' not found in mapping for key={key}")
                modified_actions.append(key_map[a])
            print("g_node", g_node.actions)

            # Reference actions come from the reference node (the canonical order/names)
            ref_actions = r_node.actions

            # This will set g_node.actions = ref_actions and re-key children/probs accordingly

            print("modified_actions", modified_actions)
            update_current_nodes(g_node, modified_actions, ref_actions)

        # After update, enqueue children in current dict order (now aligned with reference order)
        if len(r_node.children) != len(g_node.children):
            raise ValueError("Children count mismatch after update.")

        for r_child, g_child in zip(r_node.children.values(), g_node.children.values()):
            q_ref.append(r_child)
            q_gen.append(g_child)

    if q_ref or q_gen:
        raise ValueError("Tree size mismatch: traversal ended unevenly.")


def match_names_then_update_tree(ref_game, gen_game, model: str):
    """
    ref_game, gen_game are GameTree objects.
    Assumes you already implemented game.get_total_unique_actions() returning:
      {"chance": [...], 1: [...], 2: [...], ...}
    """
    ref_total = ref_game.get_total_unique_actions()
    gen_total = gen_game.get_total_unique_actions()

    mappings = build_global_action_mappings(ref_total, gen_total, model)

    print(mappings)

    traverse_and_update(ref_game.root, gen_game.root, mappings)
