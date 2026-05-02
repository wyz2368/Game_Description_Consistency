import os
from llm import call_llm, extract_python_code, save_code_to_file
from .prompts import code_generation_prompt, infer_CoT
import io
import contextlib
import traceback
from typing import Dict, Any


def append_to_log(log_path: str, title: str, content: str) -> None:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"{title}\n")
        f.write(f"{'=' * 80}\n")
        f.write(content if content.strip() else "[EMPTY]")
        if not content.endswith("\n"):
            f.write("\n")


def infer_game_tree_CoT(
    game_description: str,
    output_dir: str,
    model: str = "gpt-5-mini",
    max_attempts: int = 3,
    temperature: float = 0.0,
) -> int:
    os.makedirs(output_dir, exist_ok=True)
    output_dir = os.path.abspath(output_dir)

    log_path = os.path.join(output_dir, "llm_log.txt")
    stderr_path = os.path.join(output_dir, "stderr.txt")

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("LLM log\n")

    if os.path.exists(stderr_path):
        os.remove(stderr_path)

    instructions = code_generation_prompt()
    re_prompt = infer_CoT()
    prompt = f"{instructions}\n\nGame description:\n{game_description}\n\n{re_prompt}"

    message_pool = [{"role": "user", "content": prompt}]
    append_to_log(log_path, "INITIAL PROMPT", prompt)

    response = call_llm(
        message_pool,
        model=model,
        temperature=temperature,
    )
    append_to_log(log_path, "LLM RESPONSE - ATTEMPT 1", response)

    code = extract_python_code(response)
    save_code_to_file(code, os.path.join(output_dir, "game_tree.py"))

    for attempt in range(1, max_attempts + 1):
        stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
        old_cwd = os.getcwd()

        try:
            os.chdir(output_dir)

            exec_globals: Dict[str, Any] = {"__name__": "__main__"}

            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                exec(code, exec_globals)

            return 1

        except Exception:
            tb = traceback.format_exc()

            with open(stderr_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"ATTEMPT {attempt}\n")
                f.write(f"{'=' * 80}\n")

                stderr_text = stderr_buf.getvalue()
                if stderr_text.strip():
                    f.write("STDERR:\n")
                    f.write(stderr_text)
                    if not stderr_text.endswith("\n"):
                        f.write("\n")
                    f.write("\n")

                f.write("TRACEBACK:\n")
                f.write(tb)
                if not tb.endswith("\n"):
                    f.write("\n")

            append_to_log(log_path, f"EXECUTION ERROR - ATTEMPT {attempt}", tb)

            if attempt >= max_attempts:
                append_to_log(log_path, "FINAL RESULT", "Code generation failed after maximum retries.")
                return 0

            message_pool.append({"role": "assistant", "content": response})

            debug_prompt = (
                "Your code contains an error. Please review and fix it before trying again.\n\n"
                f"{tb}"
            )
            message_pool.append({"role": "user", "content": debug_prompt})

            append_to_log(log_path, f"DEBUG PROMPT - ATTEMPT {attempt + 1}", debug_prompt)

            response = call_llm(
                message_pool,
                model=model,
                temperature=temperature,
            )
            append_to_log(log_path, f"LLM RESPONSE - ATTEMPT {attempt + 1}", response)

            code = extract_python_code(response)
            save_code_to_file(code, os.path.join(output_dir, f"game_tree_retry_{attempt + 1}.py"))

        finally:
            os.chdir(old_cwd)

    return 0