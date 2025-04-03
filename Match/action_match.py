from google import genai
from Tree import Node, NodeType
from typing import List, Tuple
from .utils import extract_python_code


client = genai.Client(api_key="") # Add your API key here

def get_current_level_actions(node: Node, level: int = 0) -> List[Tuple[List[str], List[str], int]]:
    unique_actions = []

    if node.actions:
        
        unique_actions.append((node.actions, node.player, level, node.information_set))  # Store one representative action

    return unique_actions


def get_current_level_actions_llm(node: Node, ref_actions: List[Tuple[List[str], int, int]], level: int = 0) -> List[Tuple[List[str], List[str], int, int]]:
    unique_actions_original = []
    unique_actions_modified = []

    if node.actions:

        original_actions = node.actions[:]

        unique_actions_original.append((node.actions, node.player, level, node.information_set))  # Store one representative action

        ref_actions_for_level = [actions for actions, p, lvl, info in ref_actions 
                        if lvl == level and p == node.player and info == node.information_set]


        if ref_actions_for_level:

            prompt_check_valid = (f"You are given two lists of actions\\"
                        f"Generated Actions: {original_actions}"
                        f"Reference Actions: {ref_actions_for_level[0]}"
                        f"The actions may have different names and orders. Check if they represent the same set of actions."
                        f"Output ONLY True if they match and False otherwise.")

            response_check = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=[prompt_check_valid])
            
            print(response_check.text)
            if response_check.text.strip() == "False":
                raise ValueError("The actions in the generated game do not match the actions in the reference game.")

            prompt = (f"Given the following reference game actions from a game tree: {ref_actions_for_level[0]}. "
                        f"Modify the following generated game actions: {original_actions} to be consistent with the reference game actions, "
                        f"without changing the order of the actions. Provide the modified actions as a Python list. Only output the python list please.")
            response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=[prompt])
            print(response.text)
            modified_actions = extract_python_code(response.text)
            unique_actions_modified.append((modified_actions, node.player, level, node.information_set))  # Store one representative action    

    return unique_actions_original, unique_actions_modified

def update_current_nodes(node: Node, modified_actions_list: List[Tuple[List[str], int, int, int]], ref_actions: List[Tuple[List[str], int, int]]):
    
    modified_actions, _, _, _ = modified_actions_list[0]
    actions, _, _, _ = ref_actions[0]

    if node.node_type == NodeType.PLAYER:
        node.actions = actions
        new_children = {}
        old_children = list(node.children.values())
        for action in actions:
            for mod_action, child in zip(modified_actions, old_children):
                if action == mod_action:
                    new_children[action] = child
        node.children = new_children
    
    elif node.node_type == NodeType.CHANCE:
        node.actions = actions
        new_children = {}
        old_children = list(node.children.values())
        old_probs = node.probs
        new_probs = {}

        for action in actions:
            for mod_action, child, (old_action, prob) in zip(modified_actions, old_children, old_probs.items()):
                if action == mod_action:
                    new_children[action] = child
                    new_probs[action] = prob

        node.children = new_children
        node.probs = new_probs
