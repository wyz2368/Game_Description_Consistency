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

    ## TODO: Add also the match for chance nodes
    if node.node_type == NodeType.PLAYER and node.actions:
        info_set_id = node.information_set  # Identify information set

        # If this information set is not yet recorded at this level, store one action
        if info_set_id is not None:
            unique_actions.append((node.actions, node.player, level, node.information_set))  # Store one representative action

    return unique_actions



def get_unique_actions_by_level(
    node: Node, 
    level: int = 0, 
) -> List[Tuple[List[str], List[str], int, int]]:
    """Retrieve unique actions from a given node and its children at a specified level.
    
    Args:
        node (Node): The node from which to retrieve unique actions.
        level (int, optional): The current level in the node hierarchy. Defaults to 0.
    
    Returns:
        List[Tuple[List[str], List[str], int, int]]: A list of unique actions represented as tuples,
        where each tuple contains:
            - A list of actions (List[str]): The actions associated with the node.
            - A list of players (List[str]): The players associated with the actions.
            - An integer representing the current level (int).
            - An integer representing the information set (int).
    """

    unique_actions = []

    if node.node_type == NodeType.PLAYER and node.actions:
        info_set_id = node.information_set  # Identify information set

        # If this information set is not yet recorded at this level, store one action
        if info_set_id is not None:
            unique_actions.append((node.actions, node.player, level, node.information_set))  # Store one representative action

    # Recursively collect actions from children
    for child in node.children.values():
        unique_actions.extend(get_unique_actions_by_level(child, level + 1))

    return unique_actions

def get_current_level_actions_llm(node: Node, ref_actions: List[Tuple[List[str], int, int]], level: int = 0) -> List[Tuple[List[str], List[str], int, int]]:
    unique_actions_original = []
    unique_actions_modified = []

    if node.node_type == NodeType.PLAYER and node.actions:
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


def get_unique_actions_by_level_llm(
    node: Node, 
    ref_actions: List[Tuple[List[str], int, int]], 
    level: int = 0
) -> List[Tuple[List[str], List[str], int, int]]:
    """Retrieve unique actions from a game tree node at a specified level, modifying them based on reference actions using a language model.
    
    Args:
        node (Node): The current node in the game tree from which to retrieve actions.
        ref_actions (List[Tuple[List[str], int, int]]): A list of reference actions, each represented as a tuple containing a list of actions, a player identifier, and a level.
        level (int, optional): The current level in the game tree. Defaults to 0.
    
    Returns:
        List[Tuple[List[str], List[str], int, int]]: A tuple containing two lists:
            - unique_actions_original: A list of unique original actions collected from the node and its children.
            - unique_actions_modified: A list of modified actions that are consistent with the reference actions.
    """
    

    unique_actions_original = []
    unique_actions_modified = []

    if node.node_type == NodeType.PLAYER and node.actions:
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
                print(ref_actions_for_level[0])
                print(original_actions)
                prompt = (f"Given the following reference game actions from a game tree: {ref_actions_for_level[0]}. "
                          f"Modify the following generated game actions: {original_actions} to be consistent with the reference game actions, "
                          f"without changing the order of the actions. Provide the modified actions as a Python list. Only output the python list please.")
                response = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=[prompt])
                modified_actions = extract_python_code(response.text)
                unique_actions_modified.append((modified_actions, node.player, level, node.information_set))  # Store one representative action       

    
    # Recursively collect actions from children
    for child in node.children.values():
        uo, um = get_unique_actions_by_level_llm(child, ref_actions, level + 1)
        unique_actions_original.extend(uo)
        unique_actions_modified.extend(um)

    return unique_actions_original, unique_actions_modified

def update_current_nodes(node: Node, modified_actions_list: List[Tuple[List[str], int, int, int]]):
    # TODO: Add also the chance node
    if node.node_type == NodeType.PLAYER:
        for modified_actions, player, lvl, info_set in modified_actions_list:
            node.actions = modified_actions
            new_children = {}
            old_children = list(node.children.values())
            # Ensure a one-to-one mapping: zip may drop extra children if lengths differ.
            for action, child in zip(modified_actions, old_children):
                new_children[action] = child
            node.children = new_children
    

def update_nodes_with_modified_actions(node: Node, modified_actions_list: List[Tuple[List[str], int, int, int]], level: int = 0):
    """Update the actions of a node and its children based on a list of modified actions.
    
    This function traverses a tree of nodes, updating the actions of nodes of type PLAYER that match
    the specified level, player, and information set with the corresponding modified actions from the
    provided list. It also recursively updates the children of the node.
    
    Args:
        node (Node): The node to be updated.
        modified_actions_list (List[Tuple[List[str], int, int, int]]): A list of tuples where each tuple
            contains a list of modified actions, a player identifier, a level, and an information set.
        level (int, optional): The current level in the tree. Defaults to 0.
    
    Returns:
        None: This function modifies the node in place and does not return a value.
    """
    if node.node_type == NodeType.PLAYER:
        for modified_actions, player, lvl, info_set in modified_actions_list:
            if lvl == level and player == node.player and info_set == node.information_set:
                node.actions = modified_actions
                new_children = {}
                old_children = list(node.children.values())
                # Ensure a one-to-one mapping: zip may drop extra children if lengths differ.
                for action, child in zip(modified_actions, old_children):
                    new_children[action] = child
                node.children = new_children
                # Found a matching tuple for this node; update done.
                break

    # Recursively update children at the next level.
    for child in node.children.values():
        update_nodes_with_modified_actions(child, modified_actions_list, level + 1)

def match_actions(ref_node: Node, gen_node: Node):
    """Match actions between a reference game tree and a generated game tree.
    
    This function retrieves unique actions from both the reference and generated game trees, compares them, and updates the generated game tree with modified actions based on the reference.
    
    Args:
        ref_node (Node): The root node of the reference game tree.
        gen_node (Node): The root node of the generated game tree.
    
    Returns:
        Node: The updated generated game tree with modified actions.
    """
    # Get unique actions by level from the reference game tree
    ref_unique_actions = get_unique_actions_by_level(ref_node)

    # Get unique actions by level from the generated game tree
    gen_unique_actions_original, gen_unique_actions_modified = get_unique_actions_by_level_llm(gen_node, ref_unique_actions)
    print(ref_unique_actions)
    print(gen_unique_actions_original)
    print(gen_unique_actions_modified)

    # Update the generated game tree with the modified actions
    update_nodes_with_modified_actions(gen_node, gen_unique_actions_modified)

    return gen_node

