from typing import List, Tuple, Dict, Optional
from collections import defaultdict

from dataclasses import dataclass
from enum import Enum
from copy import deepcopy

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
    level_player_map = {}
    for actions, player, level, info_set in node_list:
        if level not in level_player_map:
            level_player_map[level] = player
        else:
            if level_player_map[level] != player:
                raise ValueError(f"Conflicting players found for level {level}")
    return level_player_map

def reorder_generated_game(reference_node, generated_node):
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
    node.level = level
    for child in node.children.values():
        assign_all_levels(child, level + 1)

def filter_simultaneous_moves(ref_node: Node, gen_node: Node, tree):
    ref_info_sets = {child.information_set for child in ref_node.children.values() if child.information_set is not None}
    gen_info_sets = {child.information_set for child in gen_node.children.values() if child.information_set is not None}

    ref_has_terminal = any(child.node_type == NodeType.TERMINAL for child in ref_node.children.values())
    gen_has_terminal = any(child.node_type == NodeType.TERMINAL for child in gen_node.children.values())

    start_filter = False
    start_node_ref = None
    start_node_gen = None
    level_diff = 0
    
    print(gen_node.player)
    print(gen_info_sets)
    print(gen_has_terminal)

    if len(ref_info_sets) == 1 and len(gen_info_sets) == 1 and not ref_has_terminal and not gen_has_terminal:
        start_filter = True
        start_node_ref = ref_node
        start_node_gen = gen_node

        current_level = ref_node.level
        nodes_to_check = [ref_node]
        gen_nodes_to_check = [gen_node]
        
        while nodes_to_check and gen_nodes_to_check:
            next_level_nodes = []
            next_level_gen_nodes = []

            for r_node, g_node in zip(nodes_to_check, gen_nodes_to_check):
                ref_info_sets = {child.information_set for child in r_node.children.values() if child.information_set is not None}
                gen_info_sets = {child.information_set for child in g_node.children.values() if child.information_set is not None}

                ref_has_terminal = any(child.node_type == NodeType.TERMINAL for child in r_node.children.values())
                gen_has_terminal = any(child.node_type == NodeType.TERMINAL for child in g_node.children.values())
                
                if ref_has_terminal or gen_has_terminal:
                    continue  # Skip this branch if a terminal node is found

                if len(ref_info_sets) != 1 or len(gen_info_sets) != 1:
                    continue

                if not r_node.children or not g_node.children:
                    continue

                # Mark the current nodes as checked
                r_node.checked = True
                g_node.checked = True

                # Mark all children as checked
                for child in r_node.children.values():
                    child.checked = True
                    next_level_nodes.append(child)
                for child in g_node.children.values():
                    child.checked = True
                    next_level_gen_nodes.append(child)
                
                ## Store the path for each children
                

            nodes_to_check = next_level_nodes
            gen_nodes_to_check = next_level_gen_nodes
            level_diff += 1
        
        # Switch the final nodes of children.
        
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
        for action in start_node_gen.actions:
            if action in start_node_gen.children:
                child = start_node_gen.children[action]
                collect_paths(child, [action])

        # Debugging output
        for p, c in children_paths.items():
            print(f"Path: {p}")
            print(f"Node: {c}")
        
        print(start_node_gen.actions)
        new_gen = reorder_generated_game(start_node_ref, start_node_gen)
        print(new_gen)
        
        
        update_nodes_with_switching_order(start_node_gen, new_gen, level=start_node_gen.level)

        # tree.print_tree()

        # final_nodes_with_paths = {}

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
                    print(f"Final Path: {final_path}")
                    for original_path, original_node in children_paths.items():
                        if final_path == original_path:
                            # print("Original Node", original_node)
                            # print(node)
                            node.children[action] = original_node

        # Start collecting final nodes from each action of the start node
        # for action in start_node_gen.actions:
        #     print(action)
        #     if action in start_node_gen.children:
        #         # print("action")
        #         child = start_node_gen.children[action]
        #         collect_paths_new(child, [action])

        for action, child in start_node_gen.children.items():
            collect_paths_new(child, [action])  
        
        # for path, node in final_nodes_with_paths.items():
        #     print(f"Path: {path}")
        #     print(f"Node: {node}")

    if start_filter:
        print(f"Simultaneous move game starts at node {start_node_ref.label} and lasts for {level_diff} levels")
        return

    for ref_child, gen_child in zip(ref_node.children.values(), gen_node.children.values()):
        if not getattr(ref_child, 'checked', False) and not getattr(gen_child, 'checked', False):
            filter_simultaneous_moves(ref_child, gen_child, tree)


def switch_order(ref_node: Node, gen_node: Node, tree):

    assign_all_levels(ref_node)
    assign_all_levels(gen_node)

    # tree.print_tree()

    filter_simultaneous_moves(ref_node, gen_node, tree)