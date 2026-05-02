from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Union
from pathlib import Path
import traceback
import json
import math
import hashlib

import pygambit as gbt
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pygambit-generation")

GAMES: Dict[str, gbt.Game] = {}

# =========================
# Helpers
# =========================

def get_game(game_id: str) -> gbt.Game:
    if game_id not in GAMES:
        raise ValueError(f"Unknown game_id: {game_id}")
    return GAMES[game_id]


def path_to_str(path: Sequence[str]) -> str:
    return "root" if not path else " / ".join(path)


def ensure_player(g: gbt.Game, player: str):
    if player == "chance":
        return g.players.chance

    for p in g.players:
        label = getattr(p, "label", None)
        if label == player or str(p) == player:
            return p

    try:
        return g.players.add(player)
    except Exception:
        pass

    raise ValueError(f"Unknown player: {player}")


def coerce_prob(x: Union[int, float, str]):
    if isinstance(x, str) and "/" in x:
        frac = Fraction(x)
        return gbt.Rational(frac.numerator, frac.denominator)
    return x


def resolve_node_by_path(g: gbt.Game, path: Sequence[str]):
    node = g.root
    for action in path:
        try:
            node = node.children[action]
        except Exception as e:
            raise ValueError(
                f"Cannot resolve path {path_to_str(path)} at action '{action}'"
            ) from e
    return node


def is_terminal(node: Any) -> bool:
    return node.is_terminal


def serialize_payoff(x: Any) -> str:
    return str(x)


def serialize_outcome(g: gbt.Game, outcome) -> Optional[Dict[str, Any]]:
    if outcome is None:
        return None

    return {
        "label": outcome.label,
        "payoffs": [serialize_payoff(outcome[p]) for p in g.players],
    }


def find_outcome_by_label(g: gbt.Game, label: str):
    for o in g.outcomes:
        if getattr(o, "label", None) == label or str(o) == label:
            return o
    raise ValueError(f"Unknown outcome: {label}")


def _make_jsonable(value: Any) -> Any:
    """
    Convert common Python values into JSON-safe values.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _make_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_make_jsonable(v) for v in value]
    return str(value)


# =========================
# MCP tools
# =========================

@mcp.tool()
def create_new_tree_game(
    game_id: str,
    title: str = "",
    players: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new extensive-form game."""
    if game_id in GAMES:
        raise ValueError(f"game_id already exists: {game_id}")

    if players:
        g = gbt.Game.new_tree(players=players, title=title)
    else:
        g = gbt.Game.new_tree(title=title)

    GAMES[game_id] = g
    return {
        "ok": True,
        "game_id": game_id,
        "title": title,
        "players": players or [],
    }


@mcp.tool()
def get_outcome(game_id: str, path: List[str]) -> Dict[str, Any]:
    """Return outcome for a terminal node."""
    g = get_game(game_id)
    node = resolve_node_by_path(g, path)
    if not is_terminal(node):
        raise ValueError(f"Path {path_to_str(path)} is not terminal")
    return {
        "path": path,
        "outcome": serialize_outcome(g, getattr(node, "outcome", None)),
    }


@mcp.tool()
def append_move_at_path(
    game_id: str,
    path: List[str],
    player: str,
    actions: List[str],
) -> Dict[str, Any]:
    """Add a move at a terminal node identified by action-label path."""
    g = get_game(game_id)
    node = resolve_node_by_path(g, path)

    if not is_terminal(node):
        raise ValueError(f"Path {path_to_str(path)} is not terminal")

    g.append_move(node, ensure_player(g, player), actions)

    return {
        "ok": True,
        "path": path,
        "player": player,
        "actions": actions,
        "children": {a: list(path) + [a] for a in actions},
    }


@mcp.tool()
def append_move_at_paths_as_infoset(
    game_id: str,
    paths: List[List[str]],
    player: str,
    actions: List[str],
) -> Dict[str, Any]:
    """
    Add the same move at multiple terminal nodes, placing them in one new infoset.
    Equivalent to g.append_move([node1, node2, ...], player, actions).
    """
    g = get_game(game_id)
    nodes = [resolve_node_by_path(g, path) for path in paths]

    for node, path in zip(nodes, paths):
        if not is_terminal(node):
            raise ValueError(f"Path {path_to_str(path)} is not terminal")

    g.append_move(nodes, ensure_player(g, player), actions)

    return {
        "ok": True,
        "paths": paths,
        "player": player,
        "actions": actions,
        "children": [
            {a: list(path) + [a] for a in actions}
            for path in paths
        ],
    }


@mcp.tool()
def append_chance_move_at_path(
    game_id: str,
    path: List[str],
    actions: List[str],
    probs: List[Union[int, float, str]],
) -> Dict[str, Any]:
    """Add a chance move at path and set probabilities. If a chance move assigns probability 0 to an action, do not include that action or its branch in the game tree."""
    if len(actions) != len(probs):
        raise ValueError("actions and probs must have same length")

    g = get_game(game_id)
    node = resolve_node_by_path(g, path)

    if not is_terminal(node):
        raise ValueError(f"Path {path_to_str(path)} is not terminal")

    coerced = [coerce_prob(p) for p in probs]

    total = sum(Fraction(str(p)) if not isinstance(p, str) else Fraction(p) for p in probs)
    if total != 1:
        raise ValueError("Chance probabilities must sum exactly to 1")

    g.append_move(node, g.players.chance, actions)
    g.set_chance_probs(node.infoset, coerced)

    return {
        "ok": True,
        "path": path,
        "actions": actions,
        "probs": probs,
        "children": {a: list(path) + [a] for a in actions},
    }


@mcp.tool()
def set_outcome_at_path(
    game_id: str,
    path: List[str],
    payoffs: Optional[List[Any]] = None,
    label: str = "",
) -> Dict[str, Any]:
    """
    Create a new outcome and assign it to the node at path.
    Also works for nonterminal outcomes if you use that pattern.
    """
    g = get_game(game_id)
    node = resolve_node_by_path(g, path)

    outcome = g.add_outcome(payoffs=payoffs, label=label)
    g.set_outcome(node, outcome)

    return {
        "ok": True,
        "path": path,
        "outcome": serialize_outcome(g, outcome),
    }


@mcp.tool()
def assign_existing_outcome_at_path(
    game_id: str,
    path: List[str],
    outcome_label: str,
) -> Dict[str, Any]:
    """Assign an existing outcome by label to the node at path."""
    g = get_game(game_id)
    node = resolve_node_by_path(g, path)
    outcome = find_outcome_by_label(g, outcome_label)
    g.set_outcome(node, outcome)

    return {
        "ok": True,
        "path": path,
        "outcome": serialize_outcome(g, outcome),
    }


@mcp.tool()
def make_infoset_from_paths(
    game_id: str,
    paths: List[List[str]],
) -> Dict[str, Any]:
    """Merge existing nodes into the same infoset using the first node's infoset."""
    if len(paths) < 2:
        raise ValueError("Need at least 2 paths")

    g = get_game(game_id)
    nodes = [resolve_node_by_path(g, path) for path in paths]

    target_infoset = getattr(nodes[0], "infoset", None)
    if target_infoset is None:
        raise ValueError("First node has no infoset")

    for node in nodes[1:]:
        g.set_infoset(node, target_infoset)

    return {
        "ok": True,
        "paths": paths,
    }


@mcp.tool()
def validate_game(game_id: str) -> Dict[str, Any]:
    """Traverse tree and report terminal nodes that have no outcome."""
    g = get_game(game_id)
    unresolved: List[List[str]] = []

    def dfs(node: Any, path: List[str]):
        try:
            children = list(node.children)
        except Exception:
            children = []

        if is_terminal(node):
            if getattr(node, "outcome", None) is None:
                unresolved.append(path.copy())
            return

        for child in children:
            prior_action = getattr(child, "prior_action", None)
            label = getattr(prior_action, "label", None) or str(prior_action)
            dfs(child, path + [label])

    dfs(g.root, [])

    return {
        "ok": True,
        "all_terminal_nodes_have_outcomes": len(unresolved) == 0,
        "unresolved_terminal_nodes": unresolved,
    }


@mcp.tool()
def save_efg(game_id: str, filepath: str) -> Dict[str, Any]:
    """Save a game as an .efg file."""
    g = get_game(game_id)
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    g.to_efg(path)
    return {
        "ok": True,
        "game_id": game_id,
        "filepath": str(path),
    }


@mcp.tool()
def run_python_for_payoff(
    code: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a short Python snippet for complex payoff calculation.

    The snippet must assign the final value to a variable named `result`.

    Available modules/helpers:
      - math
      - hashlib
      - Fraction
      - context (dict provided by caller)
    
    Do not use import statements. Use the preloaded modules directly: math, hashlib, Fraction.

    Example:
        x = int(context["n"])
        result = hashlib.sha256(str(x).encode()).hexdigest()

    Or:
        a = 2**200
        b = 3**120
        result = a - b
    """
    safe_globals = {
        "__builtins__": {
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "sorted": sorted,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "pow": pow,
            "round": round,
        },
        "math": math,
        "hashlib": hashlib,
        "Fraction": Fraction,
    }

    local_vars = {
        "context": context or {}
    }

    try:
        exec(code, safe_globals, local_vars)
    except Exception as e:
        raise ValueError(f"Python execution failed: {e}") from e

    if "result" not in local_vars:
        raise ValueError("Code must assign the final value to a variable named 'result'")

    result = _make_jsonable(local_vars["result"])

    # Validate that result is serializable
    try:
        json.dumps(result)
    except Exception as e:
        raise ValueError(f"Result is not JSON serializable: {e}") from e

    return {
        "ok": True,
        "result": result,
    }


if __name__ == "__main__":
    try:
        mcp.run(transport="stdio")
    except Exception:
        traceback.print_exc()