from openai import OpenAI
import os
import re


GPT_FAMILY_MODELS = {"gpt-5", "gpt-5-mini", "gpt-5.4", "gpt-5.4-mini"}


def _build_client(model: str):
    if model in {"deepseek", "deepseek-chat"}:
        return OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        ), "deepseek-chat", None

    if "/" in model:
        return OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        ), model, {
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-OpenRouter-Title": os.getenv("OPENROUTER_SITE_NAME", "LocalApp"),
        }

    return OpenAI(api_key=os.getenv("OPENAI_API_KEY")), model, None


def call_llm(
    prompt_or_messages,
    model: str = "gpt-5-mini",
    temperature: float = 0.0,
):
    """
    Accepts either:
        - a single string prompt
        - or a list of chat messages

    Supports:
        - OpenAI API models
        - DeepSeek direct API
        - OpenRouter models
    """

    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = prompt_or_messages

    client, api_model, extra_headers = _build_client(model)

    response = client.chat.completions.create(
        model=api_model,
        messages=messages,
        temperature=1.0
        if api_model in GPT_FAMILY_MODELS
        else temperature,
        extra_headers=extra_headers,
    )

    content = response.choices[0].message.content
    return content.strip() if content else ""

def extract_python_code(text: str):
    code_blocks = re.findall(r"```python\s*(.*?)```", text, re.DOTALL)
    return code_blocks[0].strip() if code_blocks else text


def save_code_to_file(content: str, filename: str):
    parent = os.path.dirname(filename)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
