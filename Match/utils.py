import ast
import re
from typing import List, Tuple, Dict, Any, Union, Optional
from pathlib import Path
import json

def safe_extract_player_list(response: str):
    """
    Attempts to extract a list of player names from an LLM response.

    1. Tries to find and parse a Python list in a Markdown code block.
    2. Falls back to parsing the entire response string directly.
    3. Ensures the result is a list of strings.

    Args:
        response (str): LLM response containing a list.

    Returns:
        List[str]: Extracted list of player names.

    Raises:
        ValueError: If parsing fails or result is not a valid list of strings.
    """
    # Try extracting from a markdown code block
    code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
    if code_blocks:
        code_str = code_blocks[0].strip()
    else:
        code_str = response.strip()

    try:
        parsed = ast.literal_eval(code_str)
        if isinstance(parsed, list) and all(isinstance(p, str) for p in parsed):
            return parsed
        else:
            raise ValueError("Parsed content is not a valid list of strings.")
    except Exception as e:
        raise ValueError(f"Failed to parse response as a list of strings: {e}\nResponse was: {response}")


def load_constraints_from_json_files(
    constraint_paths: Optional[List[Union[str, Path]]],
) -> List[Dict[str, Any]]:
    """
    Loads constraints from many JSON files.

    Supports either:
    1. one JSON object per file:
        {"Cst Type": 2, "Path": {...}}

    2. a list of JSON objects per file:
        [
            {"Cst Type": 2, "Path": {...}},
            {"Cst Type": 2, "Path": {...}}
        ]
    """
    if not constraint_paths:
        return []

    constraints = []

    for path in constraint_paths:
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Constraint JSON file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            constraints.append(data)
        elif isinstance(data, list):
            constraints.extend(data)
        else:
            raise ValueError(
                f"Constraint JSON file must contain a dict or list of dicts: {path}"
            )

    return constraints


def extract_type2_tsm_path_from_constraint(
    constraint: Dict[str, Any],
) -> List[Tuple[str, str]]:
    """
    Extracts the TSM start history path from one Type-2 constraint.

    The output style matches get_path_to_node:

        [("Gambler", "Enter"), ("Dealer", "Call")]

    Only path steps with an "action" are included.

    A final step such as:
        {"type": "Decision", "player": "Dealer"}

    is not included, because it identifies the node reached after the
    previous history, rather than an action taken to reach that node.
    """
    if constraint.get("Cst Type") != 2:
        raise ValueError("This function only accepts Type-2 constraints.")

    if "Path" not in constraint:
        raise ValueError("Type-2 constraint is missing 'Path'.")

    path_dict = constraint["Path"]

    ordered_keys = sorted(path_dict.keys(), key=lambda x: int(x))

    extracted_path: List[Tuple[str, str]] = []

    for key in ordered_keys:
        step = path_dict[key]

        step_type = step.get("type")
        if step_type != "Decision":
            raise ValueError(
                f"Unsupported Type-2 path step type: {step_type}"
            )

        player = step.get("player")
        if player is None:
            raise ValueError(f"Missing player in Type-2 path step {key}.")

        # Only include steps that actually have an action.
        if "action" in step:
            action = step["action"]
            extracted_path.append((player, action))

    return extracted_path


def extract_type2_tsm_paths_from_json_files(
    constraint_paths: Optional[List[Union[str, Path]]],
) -> List[List[Tuple[str, str]]]:
    """
    Loads many JSON constraint files and extracts all Type-2 TSM start paths.

    Returns:
        [
            [("Gambler", "Enter")],
            [("Player 1", "A"), ("Player 2", "B")],
            ...
        ]
    """
    constraints = load_constraints_from_json_files(constraint_paths)

    type2_paths = []

    for constraint in constraints:
        if constraint.get("Cst Type") == 2:
            path = extract_type2_tsm_path_from_constraint(constraint)
            type2_paths.append(path)

    return type2_paths