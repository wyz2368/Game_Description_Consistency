from google import genai
from Tree import Node, NodeType
from typing import List, Tuple
from .chatbot import infer_response
from .utils import extract_python_code, convert_str_to_list, safe_extract_player_list

def get_current_level_actions_llm(node, ref_actions, model):

    if node.actions:

        original_actions = node.actions[:]
            
        print("Original actions:", original_actions)
        print("Reference actions:", ref_actions)

        prompt_check_valid = (f"You are given two lists of actions\\"
                    f"Generated Actions: {original_actions}"
                    f"Reference Actions: {ref_actions}"
                    f"Disregard the different names and orders. Check if they represent the same meaning of actions."
                    f"Output ONLY True if they match and False otherwise.")
        
        response_check = infer_response(prompt_check_valid, model)
        
        if response_check == "False":
            raise ValueError("The actions in the generated game do not match the actions in the reference game.")

        # prompt = (
        # f"You are given two lists of actions\\"
        # f"Generated Actions: {original_actions}"
        # f"Reference Actions: {ref_actions}"
        # f"The following is a list of reference game actions from a game tree: {ref_actions}\n"
        # f"Please update the names in this generated list of game actions: {original_actions} so that they match the names in the reference list.\n"
        # f"Do not change the order of items in the generated list.\n"
        # f"Only return the modified list in Python list format."
        # )
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

        print("Modified actions:", modified_actions)
        
    else:
        raise ValueError("The node does not have any actions.")
        
    return modified_actions

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
