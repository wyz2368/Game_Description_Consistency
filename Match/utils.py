import ast
import re

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

def convert_str_to_list(response):
    
    lst = ast.literal_eval(response)
    
    return lst

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
