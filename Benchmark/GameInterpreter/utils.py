import re

def extract_python_code(response: str) -> str:
    # Regular expression to find Python code within triple backticks
    code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
    
    if code_blocks:
        # Join all code blocks together
        filtered_code = '\n\n'.join(code_blocks).strip()
        return filtered_code
    else:
        # No code blocks found, return response as is
        return response.strip()