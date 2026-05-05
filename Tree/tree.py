from typing import List, Tuple, Dict, Optional, Union
from collections import defaultdict, deque 
import re
from dataclasses import dataclass
from enum import Enum

from fractions import Fraction

class NodeType(Enum):
    CHANCE = 'c'
    PLAYER = 'p'
    TERMINAL = 't'


def check_duplicate_actions(actions: List[str], node_desc: str):
    seen = set()
    duplicates = set()

    for action in actions:
        if action in seen:
            duplicates.add(action)
        seen.add(action)

    if duplicates:
        raise ValueError(
            f"Duplicate action labels are not allowed at {node_desc}: "
            f"{sorted(duplicates)}"
        )

@dataclass
class Node:
    node_type: NodeType
    label: str
    player: Optional[int] = None
    information_set: Optional[int] = None
    information_set_label: Optional[str] = None
    actions: Optional[List[str]] = None
    children: Dict[str, 'Node'] = None
    payoffs: Optional[List[float]] = None
    outcome_number: Optional[int] = None
    outcome_name: str = ""
    probs: Optional[Dict[str, float]] = None
    level: int = 0  # New attribute for level
    checked: bool = False  # New attribute to track checked nodes
    parent_action: Optional[str] = None  # New parent action reference

    # Below used for merging dummy chance nodes
    raw_actions: Optional[List[str]] = None


    def __post_init__(self):
        if self.children is None:
            self.children = {}

    def add_child(self, action: str, child: 'Node'):
        child.parent = self
        self.children[action] = child


class GameTree:
    def __init__(self, title: str, players: List[str]):
        self.title = title
        self.players = players
        self.root: Optional[Node] = None

        self.level_to_nodes = defaultdict(list)
    

    def print_tree(self, node: Optional[Node] = None, depth: int = 0):
        if node is None:
            node = self.root
            print(f"Game: {self.title}")
            print(f"Players: {', '.join(self.players)}\n")

        indent = "  " * depth
        print(f"{indent}[Level {node.level}] \n", end="")
        if node.node_type == NodeType.TERMINAL:
            print(f"{indent}Terminal {node.outcome_number}: {node.label} (Payoffs: {node.payoffs})")
        elif node.node_type == NodeType.CHANCE:
            print(f"{indent}Chance: {node.label}")
            print(f"{indent}Info set: {node.information_set} {node.information_set_label}")
            print(f"{indent}Actions and Probabilities:")
            for action, prob in node.probs.items():
                print(f"{indent}  {action}: {prob}")
        else:
            print(f"{indent}Player {node.player}: {node.label}")
            print(f"{indent}Info set: {node.information_set} {node.information_set_label}")
            print(f"{indent}Actions: {node.actions}")

        if node.children:
            for action, child in node.children.items():
                print(f"{indent}Action: {action} →")
                self.print_tree(child, depth + 1)
    
    def get_total_unique_actions(self) -> Dict[Union[int, str], List[str]]:
        """
        Traverse the whole tree and return:
            {
            "chance": [unique chance actions],
            <player_number>: [unique player actions],
            ...
            }

        Notes:
        - PLAYER nodes contribute to their player key (int).
        - CHANCE nodes contribute to the "chance" key (str).
        - TERMINAL nodes contribute nothing.
        """
        if self.root is None:
            return {}

        actions_map = defaultdict(set)
        queue = deque([self.root])

        while queue:
            node = queue.popleft()

            if node.actions:
                if node.node_type == NodeType.PLAYER and node.player is not None:
                    for a in node.actions:
                        actions_map[node.player].add(a)

            for child in node.children.values():
                queue.append(child)

        # Convert sets to sorted lists for stable output
        return {k: sorted(list(v)) for k, v in actions_map.items()}


class EFGParser:
    def __init__(self):
        self.current_line = 0
        self.current_level = 0
        self.lines = []
        self.game = None

    def parse_header(self, line: str) -> Tuple[str, List[str]]:
        match = re.match(r'EFG \d+ R "(.*?)" { (.*?) }', line)
        if not match:
            raise ValueError("Invalid EFG file header")

        title = match.group(1)
        players = re.findall(r'"([^"]*)"', match.group(2))
        return title, players

    def parse_node(self, line: str) -> Node:

        node_type = NodeType(line[0])

        if node_type == NodeType.TERMINAL:
            pattern = r'^t\s+"([^"]*)"\s+(\d+)\s+"([^"]*)"\s+\{\s*([^}]*)\s*\}\s*$'
            m = re.search(pattern, line)
            if not m:
                raise ValueError(f"The line should match terminal. Got: {line}")

            label = m.group(1)
            outcome_number = int(m.group(2))
            outcome_name = m.group(3)
            values = m.group(4)

            payoff_tokens = [token.strip() for token in values.split(',') if token.strip()]

            def parse_payoff(token: str):
                if '/' in token:
                    return float(Fraction(token))
                elif '.' in token:
                    return float(token)
                else:
                    return int(token)

            payoffs = [parse_payoff(token) for token in payoff_tokens]

            return Node(
                node_type=node_type,
                label=label,
                outcome_number=outcome_number,
                outcome_name=outcome_name,
                payoffs=payoffs
            )

        elif node_type == NodeType.CHANCE:
            pattern = r'c\s+"([^"]*)"\s+(\d+)\s+"([^"]*)"\s+\{\s*((?:"[^"]+"\s+(?:\d+/\d+|\d*\.\d+|\d+)\s*)+)\}\s+\d+'
            match = re.search(pattern, line)

            if not match:
                raise ValueError(f"The line should match chance. Got: {line}")

            label = match.group(1)
            information_set = int(match.group(2))
            information_set_label = match.group(3)
            outcomes = match.group(4)

            outcome_pattern = r'"([^"]+)"\s+(\d+/\d+|\d*\.\d+|\d+)'

            raw_actions = []
            outcomes_dict = {}

            # for action, prob_str in re.findall(outcome_pattern, outcomes):
            #     raw_actions.append(action)

            #     prob = Fraction(prob_str)
            #     if action in outcomes_dict:
            #         outcomes_dict[action] += prob
            #     else:
            #         outcomes_dict[action] = prob


            for action, prob_str in re.findall(outcome_pattern, outcomes):
                raw_actions.append(action)

                prob = Fraction(prob_str)
                outcomes_dict[action] = prob
                        
            check_duplicate_actions(
                raw_actions,
                node_desc=f'chance node "{label}", information set {information_set}'
            )

            outcomes_dict = {
                action: str(prob)
                for action, prob in outcomes_dict.items()
            }

            return Node(
                node_type=node_type,
                label=label,
                information_set=information_set,
                information_set_label=information_set_label,
                actions=list(outcomes_dict.keys()),  # 合并后的 action
                raw_actions=raw_actions,             # 原始 action 数量
                probs=outcomes_dict
            )


        elif node_type == NodeType.PLAYER:
            pattern = r'p\s+"([^"]*)"\s+(\d+)\s+(\d+)\s+"([^"]*)"\s+\{\s*((?:"[^"]+"\s*)+)\s*\}\s+(\d+)'
            match = re.search(pattern, line)


            if not match:
                raise ValueError("The line should match player.")


            label = match.group(1)
            player = int(match.group(2))
            information_set = int(match.group(3))
            information_set_label = match.group(4)
            actions_str = match.group(5)
            actions = re.findall(r'"([^"]+)"', actions_str)
            # actions = match.group(5).strip().replace('"', '').split()

            check_duplicate_actions(
                actions,
                node_desc=f'player node "{label}", player {player}, information set {information_set}'
            )

            return Node(
                node_type=node_type,
                label=label,
                player=player,
                information_set=information_set,
                information_set_label=information_set_label,
                actions=actions
            )

    def build_tree(self, node: Node, level: int = 0):
        """
        Recursively build the game tree by reading lines from self.lines
        """
        node.level = level

        if node.node_type == NodeType.TERMINAL:
            self.game.level_to_nodes[self.current_level].append(node)
            self.current_level -= 1
            return

        actions = node.raw_actions if node.raw_actions is not None else node.actions

        for action in actions:
            if self.current_line < len(self.lines):
                child = self.parse_node(self.lines[self.current_line])
                self.current_line += 1

                node.add_child(action, child)  # 重复 action 会覆盖，保留最后一个

                self.game.level_to_nodes[self.current_level].append(child)
                self.current_level += 1

                self.build_tree(child, level + 1)

        self.current_level -= 1

    def parse_file(self, filename: str) -> GameTree:
        with open(filename, 'r') as f:
            self.lines = [line.strip() for line in f if line.strip()]

        # Parse the prologue.
        title, players = self.parse_header(self.lines[0])
        self.game = GameTree(title, players)

        # Define a tuple of characters to check for
        start_characters = ('t', 'p', 'c')
        for index, line in enumerate(self.lines):
            if line.strip().startswith(start_characters):
                self.current_line = index
                break

        if self.current_line < len(self.lines):
            self.game.root = self.parse_node(self.lines[self.current_line])
            self.game.level_to_nodes[self.current_level].append(self.game.root)
            self.current_level += 1
            self.current_line += 1
            self.build_tree(self.game.root, level=0)

        return self.game
    
    def to_efg(self, node: Optional[Node] = None):
        if node is None:
            node = self.game.root

        if node.node_type == NodeType.TERMINAL:
            payoffs_str = ', '.join(map(str, node.payoffs))
            return f't "{node.label}" {node.outcome_number} "{node.outcome_name}" {{ {payoffs_str} }}'

        elif node.node_type == NodeType.CHANCE:
            actions_probs = ' '.join([f'"{a}" {p}' for a, p in node.probs.items()])
            node_str = f'c "{node.label}" {node.information_set} "{node.information_set_label}" {{ {actions_probs} }} 0'
        else:
            actions_str = ' '.join([f'"{a}"' for a in node.actions])
            node_str = f'p "{node.label}" {node.player} {node.information_set} "{node.information_set_label}" {{ {actions_str} }} 0'

        children_str = '\n'.join(self.to_efg(child) for child in node.children.values())

        return f'{node_str}\n{children_str}'

    def save_to_efg(self, output_file: str):
        with open(output_file, 'w') as f:
            f.write(f'EFG 2 R "{self.game.title}" {{ ' + ' '.join(f'"{p}"' for p in self.game.players) + ' }\n')
            f.write(self.to_efg())
    
    def collect_paths_to_terminal(self, node: Optional[Node] = None, path=None, paths=None):
        if node is None:
            node = self.game.root
        if path is None:
            path = []
        if paths is None:
            paths = []

        if node.node_type == NodeType.TERMINAL:
            paths.append((list(path), node.payoffs))
        else:
            for action, child in node.children.items():
                self.collect_paths_to_terminal(child, path + [action], paths)

        return paths


Actor = Union[int, str]
PathKey = Tuple[Tuple[Actor, str], ...]


def parse_prob(prob) -> Fraction:
    """
    Safely parse probability values stored as int, float, Fraction,
    or strings like '1/2' or '0.5'.

    Returns a Fraction so comparisons are exact.
    """
    if isinstance(prob, Fraction):
        return prob

    return Fraction(str(prob))


def collect_chance_nodes_by_path(
    node: Node,
    path: Optional[List[Tuple[Actor, str]]] = None,
    chance_map: Optional[Dict[PathKey, Dict[str, Fraction]]] = None
) -> Dict[PathKey, Dict[str, Fraction]]:
    """
    Collect all chance nodes in the tree.

    Key:
        path to the chance node, including both player and chance actions:
        (
            (1, "A"),
            ("chance", "High"),
            (2, "L")
        )

    Value:
        dictionary mapping chance action -> probability:
        {
            "Heads": Fraction(1, 2),
            "Tails": Fraction(1, 2)
        }
    """

    if path is None:
        path = []

    if chance_map is None:
        chance_map = {}

    if node.node_type == NodeType.CHANCE:
        chance_map[tuple(path)] = {
            action: parse_prob(prob)
            for action, prob in node.probs.items()
        }

    for action, child in node.children.items():
        if node.node_type == NodeType.PLAYER:
            actor = node.player
        elif node.node_type == NodeType.CHANCE:
            actor = "chance"
        else:
            continue

        next_path = path + [(actor, action)]
        collect_chance_nodes_by_path(child, next_path, chance_map)

    return chance_map

def compare_chance_probs(tree1: GameTree, tree2: GameTree) -> bool:
    """
    Compare chance nodes in two game trees.

    Checks both:
    1. whether chance nodes appear at the same paths;
    2. whether their action-probability distributions are the same.
    """

    chance1 = collect_chance_nodes_by_path(tree1.root)
    chance2 = collect_chance_nodes_by_path(tree2.root)

    if chance1 == chance2:
        print("The trees have the same chance nodes and probabilities at the same paths.")
        return True

    print("The trees have different chance nodes, probabilities, or paths.")

    only_in_1 = set(chance1.keys()) - set(chance2.keys())
    only_in_2 = set(chance2.keys()) - set(chance1.keys())
    common_paths = set(chance1.keys()) & set(chance2.keys())

    if only_in_1:
        print("\nChance paths only in tree 1:")
        for path in sorted(only_in_1):
            print(path, chance1[path])

    if only_in_2:
        print("\nChance paths only in tree 2:")
        for path in sorted(only_in_2):
            print(path, chance2[path])

    for path in sorted(common_paths):
        if chance1[path] != chance2[path]:
            print(f"\nDifferent chance probabilities at path {path}:")
            print("Tree 1:", chance1[path])
            print("Tree 2:", chance2[path])

    return False

def get_information_sets(node: Node, path: Optional[List[str]] = None, info_sets: Optional[Dict[Tuple[int, int], Tuple[str, ...]]] = None):
    """
    Traverse the tree and collect a mapping from (player, information_set) to the path taken to reach that node.
    """
    if path is None:
        path = []
    if info_sets is None:
        info_sets = {}

    if node.node_type == NodeType.PLAYER:
        key = (node.player, node.information_set)
        info_sets.setdefault(key, []).append(tuple(path))

    for action, child in node.children.items():
        get_information_sets(child, path + [action], info_sets)

    return info_sets


def compare_information_sets(tree1: GameTree, tree2: GameTree) -> bool:
    """
    Compare player information set structure (player, path), including frequency.
    This accounts for simultaneous or repeated info sets.
    """
    info_sets1 = get_information_sets(tree1.root)
    info_sets2 = get_information_sets(tree2.root)

    print("Tree 1 information sets:", info_sets1)
    print("Tree 2 information sets:", info_sets2)

    def to_structural_groupings(info_sets):
        groupings = []
        for (player, _), paths in info_sets.items():
            element = (player, sorted(paths))
            groupings.append(element)
        return sorted(groupings)
    
    groupings1 = to_structural_groupings(info_sets1)
    groupings2 = to_structural_groupings(info_sets2)

    print("Tree 1 grouped structural info sets:", groupings1)
    print("Tree 2 grouped structural info sets:", groupings2)

    if groupings1 == groupings2:
        print("The trees have the same information set grouping structure.")
        return True
    else:
        print("The trees have different information set grouping structure.")
        # raise ValueError("The trees have different player information sets.")
        return False

def get_path_to_node(node: Node, players: List[str]) -> List[Tuple[str, str]]:
    """
    Return the path from the root to `node` as a list of:

        (player_name_or_chance, action)

    Example:
        [
            ("Gambler", "Enter"),
            ("Dealer", "Deal High")
        ]

    Chance nodes are represented as:
        ("chance", action)

    Assumes:
        - child.parent is set
        - child.parent_action is set
        - EFG player ids are 1-based, so player 1 maps to players[0]
    """

    path = []
    current = node

    while hasattr(current, "parent"):
        parent = current.parent
        action = current.parent_action

        if action is None:
            raise ValueError("Node has parent but no parent_action.")

        if parent.node_type == NodeType.CHANCE:
            actor = "chance"

        elif parent.node_type == NodeType.PLAYER:
            if parent.player is None:
                raise ValueError("Player node has no player id.")

            player_index = parent.player - 1

            if player_index < 0 or player_index >= len(players):
                raise ValueError(
                    f"Player id {parent.player} is out of range for players list."
                )

            actor = players[player_index]

        else:
            raise ValueError("Terminal node cannot be a parent in a valid path.")

        path.append((actor, action))
        current = parent

    path.reverse()
    return path

def check_no_zero_prob_chance_branches(tree: GameTree, raise_error: bool = True) -> bool:
    """
    Check whether any chance node has a probability-0 branch.

    A chance branch with probability 0 is illegal.

    Returns:
        True if no zero-probability chance branches are found.
        False otherwise, unless raise_error=True.

    If raise_error=True:
        raises ValueError with details of all illegal branches.
    """

    if tree.root is None:
        return True

    illegal_branches = []
    queue = deque([(tree.root, [])])

    while queue:
        node, path = queue.popleft()

        if node.node_type == NodeType.CHANCE:
            for action, prob in node.probs.items():
                prob_fraction = parse_prob(prob)

                if prob_fraction == 0:
                    illegal_branches.append({
                        "chance_node_label": node.label,
                        "information_set": node.information_set,
                        "information_set_label": node.information_set_label,
                        "action": action,
                        "probability": prob,
                        "path": tuple(path),
                    })

        for action, child in node.children.items():
            if node.node_type == NodeType.PLAYER:
                actor = node.player
            elif node.node_type == NodeType.CHANCE:
                actor = "chance"
            else:
                continue

            queue.append((child, path + [(actor, action)]))

    if illegal_branches:
        message_lines = ["Illegal chance branches with probability 0 found:"]

        for branch in illegal_branches:
            message_lines.append(
                f'- Chance node "{branch["chance_node_label"]}" '
                f'(info set {branch["information_set"]}, '
                f'label "{branch["information_set_label"]}") '
                f'has action "{branch["action"]}" with probability {branch["probability"]}. '
                f'Path: {branch["path"]}'
            )

        message = "\n".join(message_lines)

        if raise_error:
            raise ValueError(message)

        print(message)
        return False

    return True