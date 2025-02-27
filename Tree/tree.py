from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import re
from dataclasses import dataclass
from enum import Enum

class NodeType(Enum):
    CHANCE = 'c'
    PLAYER = 'p'
    TERMINAL = 't'

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
        parts = line.strip().split()
        # node_type = NodeType(parts[0])

        node_type = NodeType(line[0])

        if node_type == NodeType.TERMINAL:
            # Format: t "" outcome_number "Outcome Label" { payoff1 payoff2 }

            pattern = r't\s+"(.*?)"\s+(\d+)\s+"(.*?)"\s+\{\s*([-?\d+\s,]+)\}'

            match = re.search(pattern, line)

            if not match:
                raise ValueError("The line should match terminal.")


            label = match.group(1)
            outcome_number = int(match.group(2))
            outcome_name = match.group(3)
            values = match.group(4)
            # Parse the values into a list of integers
            payoffs = list(map(int, re.findall(r'-?\d+', values)))


            return Node(
                node_type=node_type,
                label=label,
                outcome_number=outcome_number,
                outcome_name=outcome_name,
                payoffs=payoffs
            )


        elif node_type == NodeType.CHANCE:
            # Format: c "label" info_set "(info_set_label)" { "action1" prob1 "action2" prob2 ... } 0

            pattern = r'c\s+"(.*?)"\s+(\d+)\s+"(.*?)"\s+\{\s+((?:"\w+"\s+\d+\/\d+\s*)+)\}\s+(\d+)'
            match = re.search(pattern, line)

            if not match:
                raise ValueError("The line should match chance.")

            label = match.group(1)
            information_set = int(match.group(2))
            information_set_label = match.group(3)
            outcomes = match.group(4)  # Outcomes with probabilities
            outcome_pattern = r'"(\w+)"\s+(\d+/\d+)'
            outcomes_dict = {match[0]: match[1] for match in re.findall(outcome_pattern, outcomes)}


            return Node(
                node_type=node_type,
                label=label,
                information_set=information_set,
                information_set_label=information_set_label,
                actions=list(outcomes_dict.keys()),
                probs=outcomes_dict
            )


        elif node_type == NodeType.PLAYER:
            # Format: p "" player_number info_set_number "(info_set_label)" { actions } 0
            # pattern = r'p\s+"(.*?)"\s+(\d+)\s+(\d+)\s+"(.*?)"\s+\{\s+((?:"\w+"\s*)+)\}\s+(\d+)'
            # pattern = r'p\s+"([^"]*)"\s+(\d+)\s+(\d+)\s+"([^"]*)"\s+\{\s*((?:"[^"]+"\s*)+)\s*\}\s+(\d+)'
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

            return Node(
                node_type=node_type,
                label=label,
                player=player,
                information_set=information_set,
                information_set_label=information_set_label,
                actions=actions
            )

    def build_tree(self, node: Node):
        """
        Recursively build the game tree by reading lines from self.lines
        """
        if node.node_type == NodeType.TERMINAL:
            self.game.level_to_nodes[self.current_level].append(node)
            self.current_level -= 1
            return

        actions = node.actions
        for action in actions:
            # print("action:", action)
            if self.current_line < len(self.lines):
                child = self.parse_node(self.lines[self.current_line])
                # child.level = self.current_level + 1
                self.current_line += 1
                # Link node to parents.
                node.add_child(action, child)
                # Add node to level.
                self.game.level_to_nodes[self.current_level].append(child)
                self.current_level += 1
                # Build subtree.
                self.build_tree(child)

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
            self.build_tree(self.game.root)

        return self.game
    
    def to_efg(self, node: Optional[Node] = None, depth: int = 0):
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

        children_str = '\n'.join(self.to_efg(child, depth + 1) for child in node.children.values())
        return f'{node_str}\n{children_str}'

    def save_to_efg(self, output_file: str):
        with open(output_file, 'w') as f:
            f.write(f'EFG 2 R "{self.game.title}" {{ ' + ' '.join(f'"{p}"' for p in self.game.players) + ' }\n')
            f.write(self.to_efg())