from typing import List, Tuple, Dict, Set, FrozenSet, Any
from collections import defaultdict
from copy import deepcopy
from collections import deque

from functools import reduce
from operator import mul

from Tree import Node, NodeType

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
        # Loop the modified_actions_list to find the node with the same level
        for modified_actions, player, lvl, info_set in modified_actions_list:
            if lvl == level:
                # print(level)
                node.actions = modified_actions
                node.player = player
                node.information_set = info_set
                node.checked = True
                new_children = {}
                old_children = list(node.children.values())
                
                # The length of modified_actions and length of actions of old nodes may not be the same
                if len(modified_actions) != len(old_children):
                    temp_children = list(node.children.values())[0]
                    for action in modified_actions:
                        new_children[action] = deepcopy(temp_children)
                else:
                    for action, child in zip(modified_actions, old_children):
                        new_children[action] = child
                
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
    
    ref_order = get_player_per_level(reference_nodes) # Return the dictionary of player per level, such as {0: 1, 1: 2}

    # Step 2: Group generated nodes by level
    level_nodes = defaultdict(list)
    for actions, player, level, info_set in generated_nodes:
        level_nodes[player].append((actions, level, info_set))
    

    # Step 3: Reorder nodes in the generated game based on the reference game
    reordered_nodes = []
    nop_all = [1] # Number of nodes per level
    number_of_nodes_on_next_level = 1

    for level, ref_player in ref_order.items():
        if ref_player not in level_nodes:
            raise ValueError(f"Player {ref_player} missing in generated nodes.")
        # Find the node in the generated list that matches the reference player
        
        actions, _, info_set = level_nodes[ref_player][0]
        for _ in range(number_of_nodes_on_next_level):
            reordered_nodes.append((actions, ref_player, level, info_set))
        
        nop_all.append(len(actions))
        number_of_nodes_on_next_level = reduce(mul, nop_all)

    return reordered_nodes

def mark_simultaneous_move_children(start_node):
    """
    Mark the simultaneous-move block starting at start_node.

    The key change vs your version:
    - We validate the ENTIRE frontier (nodes_to_check) together as one "level",
      instead of validating each parent independently.
    - If the level is valid (same infoset + same player across all nodes), we mark
      them checked and advance to the next level.
    """
    nodes_to_check = [start_node]

    while nodes_to_check:
        # Collect all children from the whole frontier (this forms the "next level")
        next_level_nodes = []
        for node in nodes_to_check:
            next_level_nodes.extend(list(node.children.values()))

        # If nothing to expand, stop
        if not next_level_nodes:
            break

        # Stop if any terminal is present in the next level
        if any(child.node_type == NodeType.TERMINAL for child in next_level_nodes):
            break

        # Require all nodes in next level to be PLAYER nodes (adjust if you allow CHANCE here)
        if not all(child.node_type == NodeType.PLAYER for child in next_level_nodes):
            break

        # Require all nodes in next level to have infoset
        if any(child.information_set is None for child in next_level_nodes):
            break

        # Now the key: check SAME infoset and SAME player across the WHOLE next level
        info_sets = {child.information_set for child in next_level_nodes}
        players = {child.player for child in next_level_nodes}

        if len(info_sets) != 1 or len(players) != 1:
            # Not a valid simultaneous-move layer
            break

        # If we got here, this level is a valid simultaneous layer:
        # mark current frontier + next level as checked, then advance
        for node in nodes_to_check:
            node.checked = True
        for child in next_level_nodes:
            child.checked = True

        nodes_to_check = next_level_nodes


def check_simultaneous_move_start_node(node):
    
    # 1. Check the children nodes are in the same information set
    # 2. Check the children nodes doesn't have the terminal node
    # 3. Check the children nodes has the same player
    # 4. Maybe more conditions
    
    node_type = (node.node_type != NodeType.CHANCE)
    gen_info_sets = {child.information_set for child in node.children.values() if child.information_set is not None}
    gen_has_terminal = any(child.node_type == NodeType.TERMINAL for child in node.children.values())
    gen_players = {child.player for child in node.children.values() if child.node_type == NodeType.PLAYER}
    
    is_start_node = (len(gen_info_sets) == 1 and len(gen_players) == 1 and not gen_has_terminal and node_type)
    
    return is_start_node
    
############# Below is the main function for switching the order of nodes in a game tree #############

def filter_simultaneous_moves(ref_node: Node, gen_node: Node, model: str):
    """Filters simultaneous moves between a reference game node and a generated game node within a game tree.
    This function traverses the game tree, comparing nodes from the reference game with those from the generated game. It identifies simultaneous moves and ensures that the generated nodes conform to the structure and rules defined by the reference nodes. If discrepancies are found, appropriate errors are raised.
    Args:
        ref_node (Node): The reference game node to compare against.
        gen_node (Node): The generated game node to be filtered.
    
    Raises:
        ValueError: If a matching reference node cannot be found for a generated node, or if the reference node does not meet the simultaneous move condition.
    
    Returns:
        None: The function modifies the generated game node in place based on the reference game node.
    """
    
    # To do breadth first search, we need to use a double ended queue to store the nodes

    # Initially, we append the root node of the reference game and generated game to the queue
    queue_ref = deque([ref_node])  # Queue for reference game nodes
    queue_gen = deque([gen_node])  # Queue for generated game nodes

    
    while queue_gen:
        
        level_size_ref = len(queue_ref)  # Number of nodes at this level in ref game
        level_size_gen = len(queue_gen)  # Number of nodes at this level in gen game

        ref_nodes_list = []  # Store all reference nodes for this level
        

        # Pop all nodes from the reference queue
        for _ in range(level_size_ref):
            ref_nodes_list.append(queue_ref.popleft())
        
        # We need a temp list to store the reference nodes after each node is removed in ref_nodes_list
        # This temp list will be used in action matching stage with gen_nodes_list in stage 2
        ref_nodes_list_temp = []
        
        gen_nodes_list = []
        
        ###################### Stage 1: Swtiching the order of nodes for simultaneous moves ######################
        # Process each node in the generated game queue
        for _ in range(level_size_gen):
            if not ref_nodes_list:
                break  # No more reference nodes to match

            g_node = queue_gen.popleft()
            
            # Step 1: Check if the node is already checked in the simultaneous move path
            if g_node.checked:
                print("Already checked")
                gen_nodes_list.append(g_node)
                match = False
                for r_node in ref_nodes_list:
                    if r_node.parent_action == g_node.parent_action:
                        print("Matched")
                        ref_nodes_list_temp.append(r_node)
                        ref_nodes_list.remove(r_node)
                        match = True
                        break
                if not match:
                    raise ValueError(f"No matching reference node found for g_node: {g_node} with parent action {g_node.parent_action}")
                continue
            
            # Step 2: check the node is the start node of the simultaneous move
            # 1. Check the children nodes are in the same information set
            # 2. Check the children nodes doesn't have the terminal node
            # 3. Check the children nodes has the same player
            
            gen_is_start_node = check_simultaneous_move_start_node(g_node)

            # If above conditions are not met, the node is NOT the start node of the simultaneous move

            if not gen_is_start_node:
                gen_nodes_list.append(g_node)
                match = False
                rmn = None # rmn stands for reference matched node
                for r_node in ref_nodes_list:
                    if r_node.parent_action == g_node.parent_action:
                        ref_nodes_list_temp.append(r_node)
                        ref_nodes_list.remove(r_node)
                        match = True
                        rmn = r_node
                        break
                if not match:
                    raise ValueError(f"No matching reference node found for g_node with parent action")

                continue  # Skip the g_node if it doesn't satisfy the condition
          
            print("Simultaneous move detected for g_node")
            
            # Step 3: Switch the order of simultaneous moves nodes
            matched_ref_node = None

            for r_node in ref_nodes_list:
                if r_node.parent_action == g_node.parent_action:
                    matched_ref_node = r_node
                    ref_nodes_list.remove(r_node)
                    ref_nodes_list_temp.append(r_node)
                    break  # Stop searching after the first match

            # Raise an error if no matching r_node is found
            if not matched_ref_node:
                raise ValueError(f"No matching reference node found for g_node: {g_node} with parent action {g_node.parent_action}")

            print(f"Matched ref_node, Parent Action: {matched_ref_node.parent_action}")

            # Verify that matched_ref_node also meets the simultaneous move condition
            
            matched_ref_node_is_start_node = check_simultaneous_move_start_node(matched_ref_node)

            if not matched_ref_node_is_start_node:
                raise ValueError(f"Reference node {matched_ref_node} does not meet the simultaneous move condition")
            
            # Step 4: Mark all the nodes involved in the simultaneous move
            mark_simultaneous_move_children(matched_ref_node)
            mark_simultaneous_move_children(g_node)
            
            children_paths = {}

            def collect_paths(node, path):
                if not node.checked:
                    return

                if not node.children:
                    children_paths[tuple(path)] = node
                    return

                for action, child in node.children.items():
                    if node.node_type == NodeType.PLAYER:
                        step = (node.level, node.player, action)
                    else:  # CHANCE
                        step = (node.level, -1, action)

                    if child.checked:
                        collect_paths(child, path + [step])
                    else:
                        children_paths[tuple(path + [step])] = child

            
            # Start collecting paths from each action of the start node
            for action in g_node.actions:
                child = g_node.children[action]
                if g_node.node_type == NodeType.PLAYER:
                    collect_paths(child, [(g_node.level ,g_node.player, action)])
                elif g_node.node_type == NodeType.CHANCE:
                    collect_paths(child, [(g_node.level, -1, action)])
            
            new_gen = reorder_generated_game(matched_ref_node, g_node) # Get a list of reordered nodes like [(['A', 'B'], 1, 0, 1), (['C', 'D', 'E'], 2, 1, 1), (['C', 'D', 'E'], 2, 1, 1)]
            # Update the actions in the generated game to the reordered actions for this simultaneous move part
            update_nodes_with_switching_order(g_node, new_gen, level=g_node.level) 

            # To restore the original subtree from children_paths after reordering actions in g_node.
            # After reordering actions using update_nodes_with_switching_order, the structure of g_node is changed. 
            # We need to track the path first and then restore the correct children on the path.

            def collect_paths_new(node, path):
                if not node.checked:
                    return

                for action, child in node.children.items():
                    if node.node_type == NodeType.PLAYER:
                        step = (node.level, node.player, action)
                    else:  # CHANCE
                        step = (node.level, -1, action)

                    if child.checked:
                        collect_paths_new(child, path + [step])
                    else:
                        final_path = tuple(path + [step])
                        original_node = children_paths.get(final_path)
                        if original_node is not None:
                            node.children[action] = original_node

            for action, child in g_node.children.items():
                if g_node.node_type == NodeType.PLAYER:
                    collect_paths_new(child, [(g_node.level, g_node.player, action)])
                elif g_node.node_type == NodeType.CHANCE:
                    collect_paths_new(child, [(g_node.level, -1, action)])
            
            gen_nodes_list.append(g_node)
              

        ############## Stage 2: Action Matching and Updating Nodes ######################   
        for g_node, r_node in zip(gen_nodes_list,ref_nodes_list_temp):

            if len(r_node.children.values()) != len(g_node.children.values()):
                raise ValueError(f"Number of children do not match")
            
            if r_node.node_type != g_node.node_type:
                raise ValueError(f"Node types do not match")

            for action, child in r_node.children.items():
                child.parent_action = action
            
            for action, child in g_node.children.items():
                child.parent_action = action

            for ref_child, gen_child in zip(r_node.children.values(), g_node.children.values()):

                queue_ref.append(ref_child)
                queue_gen.append(gen_child)

def build_infoset_partition(
    root: Node,
    *,
    include_chance: bool = False,
    require_parent_action: bool = True,
) -> Dict[int, Set[Tuple[Tuple[int, str], ...]]]:
    """
    Returns a mapping: information_set_id -> set of node-paths (each path is a tuple of (player, action) pairs).

    Node path convention:
      - For each edge into a node, append (parent.player, child.parent_action).
      - Root has empty path.
    """
    partition: Dict[int, Set[Tuple[Tuple[int, str], ...]]] = defaultdict(set)

    stack: List[Tuple[Node, Tuple[Tuple[int, str], ...]]] = [(root, tuple())]

    while stack:
        node, path = stack.pop()

        # Record PLAYER nodes with an infoset
        if node.node_type == NodeType.PLAYER and node.information_set is not None:
            partition[node.information_set].add(path)

        # Traverse children
        for action, child in node.children.items():
            # You already set child.parent_action = action in filter_simultaneous_moves Stage 2,
            # but we can also use `action` directly from the dict.
            edge_action = getattr(child, "parent_action", None)
            if require_parent_action and edge_action is None:
                # Fall back to dict key if parent_action is not set
                edge_action = action

            if edge_action is None:
                # If still None, skip or raise; choose raise to catch inconsistencies early
                raise ValueError("Child has no parent_action and action key is None/unavailable.")

            # Typically (player, action) is parent PLAYER's identity + the edge action label
            if node.node_type == NodeType.PLAYER:
                next_path = path + ((node.player, edge_action),)
            elif node.node_type == NodeType.CHANCE:
                if include_chance:
                    next_path = path + ((-1, edge_action),)
                else:
                    # If you don't want chance in the path identity, keep the same path
                    next_path = path
            else:
                # TERMINAL has no children in normal trees, but handle generically
                next_path = path

            stack.append((child, next_path))

    return partition

def canonicalize_partition(
    part: Dict[int, Set[Tuple[Tuple[int, str], ...]]]
) -> List[FrozenSet[Tuple[Tuple[int, str], ...]]]:
    """
    Convert {infoset_id -> set(paths)} into a canonical, order-independent representation:
      a sorted list of frozensets, where each frozenset is the group of paths in one infoset.
    """
    groups = [frozenset(paths) for paths in part.values()]
    # Sort deterministically for stable comparison / debugging
    groups.sort(key=lambda g: (len(g), sorted(map(str, g))))
    return groups


def infoset_partitions_equal(ref_root: Node, gen_root: Node) -> Tuple[bool, Any]:
    """
    Returns (equal, debug_info). Comparison is ID-independent.
    debug_info contains canonical forms if not equal.
    """
    ref_part = build_infoset_partition(ref_root)
    gen_part = build_infoset_partition(gen_root)

    ref_can = canonicalize_partition(ref_part)
    gen_can = canonicalize_partition(gen_part)

    ok = (ref_can == gen_can)
    debug = None
    if not ok:
        debug = {
            "ref_num_infosets": len(ref_part),
            "gen_num_infosets": len(gen_part),
            "ref_groups": ref_can,
            "gen_groups": gen_can,
        }
    return ok, debug
            
            

def switch_order(ref_node: Node, gen_node: Node, model: str):
    """Switches the order of two nodes in a tree structure and filters simultaneous moves.
    
    Args:
        ref_node (Node): The reference node whose order is to be switched.
        gen_node (Node): The general node whose order is to be switched.
    
    Returns:
        None: This function modifies the tree in place and does not return a value.
    """

    filter_simultaneous_moves(ref_node, gen_node, model)

    ok, _ = infoset_partitions_equal(ref_node, gen_node)

    if not ok:
        raise ValueError("Generated game infoset partition does not match reference game.")