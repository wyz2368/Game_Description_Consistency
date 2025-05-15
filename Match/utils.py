import ast
import re

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
