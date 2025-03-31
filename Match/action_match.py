from google import genai
from Tree import Node, NodeType
from typing import List, Tuple, Dict, Optional
import re
import ast

client = genai.Client(api_key="") # Add your API key here

def extract_python_code(response):
    """Extracts Python code from a given response string.
    
    This function searches for Python code enclosed within triple backticks in the input string. 
    It returns the first code block as a Python list if it can be evaluated; otherwise, it returns 
    the raw code block as a string. If no code blocks are found, an empty list is returned.
    
    Args:
        response (str): The input string containing potential Python code blocks.
    
    Returns:
        list or str: The first extracted Python code block as a list if it can be evaluated, 
                     otherwise as a string. Returns an empty list if no code blocks are found.
    """
    # Regular expression to find Python code within triple backticks
    code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
    
    # Extract and clean each code block
    cleaned_blocks = [code_block.strip() for code_block in code_blocks]
    
    # Convert the first code block (assuming it's a Python list) to an actual list
    if cleaned_blocks:
        try:
            filtered_code = ast.literal_eval(cleaned_blocks[0])
        except (SyntaxError, ValueError):
            filtered_code = cleaned_blocks[0]
    else:
        filtered_code = []
    
    return filtered_code

def get_current_level_actions(node: Node, level: int = 0) -> List[Tuple[List[str], List[str], int]]:
    unique_actions = []

    if node.actions:
        info_set_id = node.information_set  # Identify information set

        # If this information set is not yet recorded at this level, store one action
        if info_set_id is not None:
            unique_actions.append((node.actions, node.player, level, node.information_set))  # Store one representative action

    return unique_actions


def get_current_level_actions_llm(node: Node, ref_actions: List[Tuple[List[str], int, int]], level: int = 0) -> List[Tuple[List[str], List[str], int, int]]:
    unique_actions_original = []
    unique_actions_modified = []

    if node.actions:
        info_set_id = node.information_set  # Identify information set

        # If this information set is not yet recorded at this level, store one action
        if info_set_id is not None:

            original_actions = node.actions[:]
            # print(original_actions)
            unique_actions_original.append((node.actions, node.player, level, node.information_set))  # Store one representative action
            modified_actions = original_actions  # Default to the same actions

            ref_actions_for_level = [actions for actions, p, lvl, info in ref_actions 
                         if lvl == level and p == node.player and info == node.information_set]

            # print(ref_actions_for_level)

            # unique_actions.append((node.actions, node.player, level))  # Store one representative action

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

                # print(ref_actions_for_level[0])
                # print(original_actions)
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
    if node.node_type == NodeType.PLAYER:
        for actions, _, _, _ in ref_actions:
            for modified_actions, player, lvl, info_set in modified_actions_list:
                node.actions = actions
                new_children = {}
                old_children = list(node.children.values())
                for action in actions:
                    for mod_action, child in zip(modified_actions, old_children):
                        if action == mod_action:
                            new_children[action] = child
                node.children = new_children
    
    if node.node_type == NodeType.CHANCE:

        for actions, _, _, _ in ref_actions:
            for modified_actions, player, lvl, info_set in modified_actions_list:
                node.actions = actions
                new_children = {}
                old_children = list(node.children.values())
                # Preserve probabilities for corresponding actions
                old_probs = node.probs
                new_probs = {}
                # Ensure a one-to-one mapping: zip may drop extra children if lengths differ.
                for action in actions:
                    for mod_action, child,  (old_action, prob) in zip(modified_actions, old_children, old_probs.items()):
                        if action == mod_action:
                            new_children[action] = child
                            new_probs[action] = prob
                node.children = new_children
                node.probs = new_probs
