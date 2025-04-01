from typing import List, Tuple, Dict, Optional
from collections import defaultdict

from dataclasses import dataclass
from enum import Enum
from copy import deepcopy
from collections import deque

from functools import reduce
from operator import mul

from Tree import Node, NodeType
from .action_match import get_current_level_actions, get_current_level_actions_llm, update_current_nodes

def update_nodes_with_switching_order(node: Node, modified_actions_list: List[Tuple[List[str], int, int, int]], level: int = 0):
    """
    Updates the actions and children keys of each Node with modified actions from unique_actions_modified.
    Ensures consistency for all nodes at the same level.
    
    Parameters:
    - node: The current Node being processed.
    - modified_actions_list: A list of tuples (modified_actions, player, level, information_set).
    - level: The current depth level in the game tree.
    """
    if node.node_type == NodeType.PLAYER:
        for modified_actions, player, lvl, info_set in modified_actions_list:
            if lvl == level:
                # print(level)
                node.actions = modified_actions
                node.player = player
                node.information_set = info_set
                node.checked = True
                new_children = {}
                old_children = list(node.children.values())

                if len(modified_actions) != len(old_children):
                    temp_children = list(node.children.values())[0]
                    for action in modified_actions:
                        new_children[action] = deepcopy(temp_children)
                else:
                    # print("Modified Actions")
                    for action, child in zip(modified_actions, old_children):
                        # print(action)
                        new_children[action] = child
                
                
                # temp_children = list(node.children.values())[0]
                # for action in modified_actions:
                #     new_children[action] = temp_children
                
                node.children = new_children
                break

    # Recursively update children at the next level
    for child in node.children.values():
        # print(level)
        update_nodes_with_switching_order(child, modified_actions_list, level + 1)

def get_unique_actions_by_level_partial_tree(
    node: Node
) -> List[Tuple[List[str], List[str], int, int]]:
    """Retrieve unique actions from a given node in a partial game tree.
    
    This function processes a node and its children to collect unique actions that are marked as checked. 
    It specifically looks for player nodes and records their actions along with relevant information such as 
    the player, level, and information set.
    
    Args:
        node (Node): The node from which to collect unique actions. It should be marked as checked.
    
    Returns:
        List[Tuple[List[str], List[str], int, int]]: A list of tuples, each containing:
            - A list of actions (List[str]): The actions available at the node.
            - A list of players (List[str]): The players associated with the actions.
            - An integer representing the level of the node (int).
            - An integer representing the information set ID (int).
    """

    unique_actions = []

    # Only process nodes that are marked as checked (part of the simultaneous move path)
    if node.checked:
        if node.node_type == NodeType.PLAYER and node.actions:
            info_set_id = node.information_set

            # If this information set is not yet recorded at this level, store one action
            if info_set_id is not None:
                unique_actions.append((node.actions, node.player, node.level, node.information_set))

        # Recursively collect actions from children
        for child in node.children.values():
            unique_actions.extend(get_unique_actions_by_level_partial_tree(child))

    return unique_actions

def get_player_per_level(node_list):
    """Get a mapping of players to their corresponding levels from a list of nodes.
    
    Args:
        node_list (list of tuples): A list where each tuple contains the following elements:
            - actions: The actions taken (not used in this function).
            - player: The player associated with the node.
            - level: The level associated with the node.
            - info_set: Additional information (not used in this function).
    
    Returns:
        dict: A dictionary mapping levels to their corresponding players.
    
    Raises:
        ValueError: If conflicting players are found for the same level.
    """
    level_player_map = {}
    for actions, player, level, info_set in node_list:
        if level not in level_player_map:
            level_player_map[level] = player
        else:
            if level_player_map[level] != player:
                raise ValueError(f"Conflicting players found for level {level}")
    return level_player_map

def reorder_generated_game(reference_node, generated_node):
    """Reorder the players in the generated game to match the reference game.
    
    This function takes two game structures, a reference game and a generated game, and reorders the players in the generated game to align with the player order of the reference game. It ensures that the generated game reflects the same player sequence and structure as defined in the reference game.
    
    Args:
        reference_node: The root node of the reference game structure.
        generated_node: The root node of the generated game structure.
    
    Returns:
        list: A list of reordered nodes representing the players in the generated game, structured to match the reference game.
    
    Raises:
        ValueError: If a player in the reference game is missing from the generated game nodes.
    """
    """Reorder the players in the generated game to match the reference game."""
    # Step 1: Get player order per level from reference game
    reference_nodes = get_unique_actions_by_level_partial_tree(reference_node)
    generated_nodes = get_unique_actions_by_level_partial_tree(generated_node)

    print(reference_nodes)
    print(generated_nodes)

    ref_order = get_player_per_level(reference_nodes)

    # Step 2: Group generated nodes by level
    level_nodes = defaultdict(list)
    for actions, player, level, info_set in generated_nodes:
        level_nodes[player].append((actions, level, info_set))

    # Step 3: Reorder nodes in the generated game based on the reference game
    reordered_nodes = []
    nop_all = [1]
    number_of_players_on_next_level = 1

    for level, ref_player in ref_order.items():
        if ref_player not in level_nodes:
            raise ValueError(f"Player {ref_player} missing in generated nodes.")
        # Find the node in the generated list that matches the reference player
        
        actions, _, info_set = level_nodes[ref_player][0]
        for _ in range(number_of_players_on_next_level):
            reordered_nodes.append((actions, ref_player, level, info_set))
        
        nop_all.append(len(actions))
        
        number_of_players_on_next_level = reduce(mul, nop_all)

    return reordered_nodes

def assign_all_levels(node: Node, level: int = 0):
    """Assigns levels to a tree structure starting from the given node.
    
    This function recursively assigns a level to each node in a tree, where the 
    level of the root node is specified by the `level` parameter. Each child node 
    is assigned a level that is one greater than its parent's level.
    
    Args:
        node (Node): The root node from which to start assigning levels.
        level (int, optional): The level to assign to the root node. Defaults to 0.
    
    Returns:
        None: This function modifies the `level` attribute of the nodes in place.
    """
    node.level = level
    for child in node.children.values():
        assign_all_levels(child, level + 1)

def mark_simultaneous_move_children(start_node):
    """Marks nodes and their children in a game tree that represent simultaneous moves.
    This function traverses the game tree starting from the given `start_node`, marking nodes that are part of simultaneous move scenarios. It filters out terminal nodes and ensures that only valid simultaneous move nodes are processed. If a node is determined to be part of a simultaneous move, it and all its children are marked as checked.
    Args:
        start_node (Node): The starting node of the game tree from which to begin marking simultaneous move nodes.
    Returns:
        None: The function modifies the nodes in place, marking them as checked.
    """
    nodes_to_check = [start_node]
    
    while nodes_to_check:
        next_level_nodes = []

        for node in nodes_to_check:
            # **Filter out terminal nodes**
            if any(child.node_type == NodeType.TERMINAL for child in node.children.values()):
                continue  # Skip processing terminal branches

            # **Ensure the node belongs to a simultaneous move**
            info_sets = {child.information_set for child in node.children.values() if child.information_set is not None}
            players = {child.player for child in node.children.values() if child.node_type == NodeType.PLAYER}

            if len(info_sets) != 1 or len(players) != 1:
                continue  # Skip if not a valid simultaneous move

            # **Mark current node and its children**
            node.checked = True
            for child in node.children.values():
                child.checked = True
                next_level_nodes.append(child)

        nodes_to_check = next_level_nodes  # Move to the next level

def filter_simultaneous_moves(ref_node: Node, gen_node: Node):
    """Filters simultaneous moves between a reference game node and a generated game node within a game tree.
    This function traverses the game tree, comparing nodes from the reference game with those from the generated game. It identifies simultaneous moves and ensures that the generated nodes conform to the structure and rules defined by the reference nodes. If discrepancies are found, appropriate errors are raised.
    Args:
        ref_node (Node): The reference game node to compare against.
        gen_node (Node): The generated game node to be filtered.
        tree: The game tree containing the nodes.
    
    Raises:
        ValueError: If a matching reference node cannot be found for a generated node, or if the reference node does not meet the simultaneous move condition.
    
    Returns:
        None: The function modifies the generated game node in place based on the reference game node.
    """
    
    queue_ref = deque([ref_node])  # Queue for reference game nodes
    queue_gen = deque([gen_node])  # Queue for generated game nodes

    

    while queue_gen:
        
        level_size_ref = len(queue_ref)  # Number of nodes at this level in ref game
        level_size_gen = len(queue_gen)  # Number of nodes at this level in gen game

        ref_nodes_list = []  # Store all reference nodes for this level
        

        # **Step 1: Pop all reference nodes for this level first**
        for _ in range(level_size_ref):
            ref_nodes_list.append(queue_ref.popleft())

        
        ref_nodes_list_temp = []
        
        
        gen_nodes_list = []
        for _ in range(level_size_gen):
            if not ref_nodes_list:
                break  # No more reference nodes to match

            # r_node = queue_ref.popleft()
            g_node = queue_gen.popleft()
            

            # print(r_node.parent_action)
            # print(g_node.parent_action)

            if g_node.checked:
                print("Already checked")
                gen_nodes_list.append(g_node)
                match = False
                for r_node in ref_nodes_list:
                    # print(r_node.parent_action)
                    if r_node.parent_action == g_node.parent_action:
                        print("Matched")
                        ref_nodes_list_temp.append(r_node)
                        ref_nodes_list.remove(r_node)
                        match = True
                        break
                if not match:
                    raise ValueError(f"No matching reference node found for g_node: {g_node.label} with parent action {g_node.parent_action}")
                continue

            gen_info_sets = {child.information_set for child in g_node.children.values() if child.information_set is not None}
            gen_has_terminal = any(child.node_type == NodeType.TERMINAL for child in g_node.children.values())
            gen_players = {child.player for child in g_node.children.values() if child.node_type == NodeType.PLAYER}

            if not (len(gen_info_sets) == 1 and len(gen_players) == 1 and not gen_has_terminal):
                # print(g_node)
                gen_nodes_list.append(g_node)
                match = False
                rmn = None
                for r_node in ref_nodes_list:
                    if r_node.parent_action == g_node.parent_action:
                        ref_nodes_list_temp.append(r_node)
                        ref_nodes_list.remove(r_node)
                        match = True
                        rmn = r_node
                        break
                if not match:
                    # print(g_node.parent_action)
                    raise ValueError(f"No matching reference node found for g_node with parent action")
                else:
                    ref_info_sets = {child.information_set for child in rmn.children.values() if child.information_set is not None}
                    ref_has_terminal = any(child.node_type == NodeType.TERMINAL for child in rmn.children.values())
                    ref_players = {child.player for child in rmn.children.values() if child.node_type == NodeType.PLAYER}
                    ref_terminal = rmn.node_type == NodeType.TERMINAL
                    if len(ref_info_sets) == 1 and len(ref_players) == 1 and not ref_has_terminal and not ref_terminal:
                        raise ValueError(f"Reference node does not meet the simultaneous move condition")

                continue  # Skip this g_node if it doesn't satisfy the condition

            print("Simultaneous move detected for g_node")

            matched_ref_node = None

            for r_node in ref_nodes_list:
                if r_node.parent_action == g_node.parent_action:
                    matched_ref_node = r_node
                    ref_nodes_list.remove(r_node)
                    ref_nodes_list_temp.append(r_node)
                    break  # Stop searching after the first match

            # **Raise an error if no matching r_node is found**
            if not matched_ref_node:
                raise ValueError(f"No matching reference node found for g_node: {g_node.label} with parent action {g_node.parent_action}")

            print(f"Matched ref_node: {matched_ref_node.label}, Parent Action: {matched_ref_node.parent_action}")

            # **Step 5: Verify that matched_ref_node also meets the simultaneous move condition**
            ref_info_sets = {child.information_set for child in matched_ref_node.children.values() if child.information_set is not None}
            ref_has_terminal = any(child.node_type == NodeType.TERMINAL for child in matched_ref_node.children.values())
            ref_players = {child.player for child in matched_ref_node.children.values() if child.node_type == NodeType.PLAYER}

            if not (len(ref_info_sets) == 1 and len(ref_players) == 1 and not ref_has_terminal):
                raise ValueError(f"Reference node {matched_ref_node.label} does not meet the simultaneous move condition")
            
            nodes_to_check = [matched_ref_node]
            gen_nodes_to_check = [g_node]
            while nodes_to_check or gen_nodes_to_check:
                next_level_nodes = []
                next_level_gen_nodes = []

                # **Mark children of ref_node and gen_node separately**
                for node in nodes_to_check:
                    mark_simultaneous_move_children(node)
                    for child in node.children.values():
                        next_level_nodes.append(child)
                
                for node in gen_nodes_to_check:
                    mark_simultaneous_move_children(node)
                    for child in node.children.values():
                        next_level_gen_nodes.append(child)
            
                nodes_to_check = next_level_nodes
                gen_nodes_to_check = next_level_gen_nodes
            
            children_paths = {}

            def collect_paths(node, path):
                """Recursively collect paths for all children of the given node."""
                if not node.checked:
                    return
                
                # If leaf node or next nodes aren't checked, store the path
                if not node.children:
                    children_paths[tuple(path)] = node
                    return
                
                for action, child in node.children.items():
                    if child.checked:
                        collect_paths(child, path + [action])
                    else:
                        children_paths[tuple(sorted(path + [action]))] = child

            
            
            # Start collecting paths from each action of the start node
            for action in g_node.actions:
                if action in g_node.children:
                    child = g_node.children[action]
                    collect_paths(child, [action])
            
            new_gen = reorder_generated_game(matched_ref_node, g_node)
            # print(new_gen)
            update_nodes_with_switching_order(g_node, new_gen, level=g_node.level)


            def collect_paths_new(node, path):
                """Recursively collect paths for all children of the given node."""
                if not node.checked:
                    return
                
                for action, child in node.children.items():
                    if child.checked:
                        collect_paths_new(child, path + [action])
                    else:
                        # print(action)
                        # final_nodes_with_paths[tuple(sorted(path + [action]))] = node
                        final_path = tuple(sorted(path + [action]))
                        for original_path, original_node in children_paths.items():
                            if final_path == original_path:
                                # print("Original Node", original_node)
                                # print(node)
                                node.children[action] = original_node
                
            for action, child in g_node.children.items():
                collect_paths_new(child, [action])
            
            gen_nodes_list.append(g_node)
            # print("Gen Nodes List", gen_nodes_list)
              
            
        for g_node, r_node in zip(gen_nodes_list,ref_nodes_list_temp):

            if len(r_node.children.values()) != len(g_node.children.values()):
                raise ValueError(f"Number of children do not match")
            
            if r_node.node_type != g_node.node_type:
                raise ValueError(f"Node types do not match")

            level = r_node.level
            ref_actions = get_current_level_actions(r_node,level)
            # gen_actions = get_current_level_actions(g_node)
            level = g_node.level
            original_list, modified_list = get_current_level_actions_llm(g_node, ref_actions, level) 
            # print("Original List", original_list)
            # print("Modified List", modified_list)
            
            print(queue_gen)
            update_current_nodes(g_node, modified_list, ref_actions)
            print(queue_gen)
            
            for action, child in r_node.children.items():
                child.parent_action = action
            
            for action, child in g_node.children.items():
                # print(action)
                child.parent_action = action

            for ref_child, gen_child in zip(r_node.children.values(), g_node.children.values()):
                # print(gen_child)

                queue_ref.append(deepcopy(ref_child))
                queue_gen.append(deepcopy(gen_child))
                # print(queue_gen)
            
            print(queue_gen)

def switch_order(ref_node: Node, gen_node: Node):
    """Switches the order of two nodes in a tree structure and filters simultaneous moves.
    
    Args:
        ref_node (Node): The reference node whose order is to be switched.
        gen_node (Node): The general node whose order is to be switched.
    
    Returns:
        None: This function modifies the tree in place and does not return a value.
    """

    assign_all_levels(ref_node)
    assign_all_levels(gen_node)

    filter_simultaneous_moves(ref_node, gen_node)