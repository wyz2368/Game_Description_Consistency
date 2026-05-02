import os
import io
import re
import pygambit as gbt
from openai import OpenAI
from utils import extract_python_code
from datetime import datetime
import contextlib
import traceback
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmark_dataset import copy_generated_efg, find_efg_for_run


def _build_client(api_key, model):
    if model in {"deepseek", "deepseek-chat"}:
        return (
            OpenAI(
                api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com",
            ),
            "deepseek-chat",
        )

    if "/" in model:
        return (
            OpenAI(
                api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            ),
            model,
        )

    return (
        OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY")),
        model,
    )


class LLMBackend:
    def __init__(self, api_key=None, model="gpt-5-mini", max_attempts=3, root_dir=None):
        print("model:", model)

        self.model = model
        self.max_attempts = max_attempts
        self.root_dir = root_dir or os.getenv("BENCHMARK_OUTPUT_DIR", "benchmark_gameinterpreter")

        self.client, self.api_model = _build_client(api_key, model)

        # These are set per run
        self.current_game_dir = None
        self.current_run_dir = None
        self.log_file = None

    # ---------------------------
    # Filesystem helpers
    # ---------------------------
    def _sanitize(self, name: str) -> str:
        """Make a safe folder name."""
        name = name.strip().lower()
        name = re.sub(r"[^a-z0-9\-\s_]", "", name)
        name = re.sub(r"\s+", "-", name)
        return name or "game"

    def _ensure_dirs_for_run(self, game_name: str):
        """Create per-game folder and a new numeric subfolder for this run: 1, 2, 3, ..."""
        game_dir = os.path.join(self.root_dir, self._sanitize(game_name))
        os.makedirs(game_dir, exist_ok=True)

        # Find the next available integer subfolder
        i = 1
        while os.path.isdir(os.path.join(game_dir, str(i))):
            i += 1

        run_dir = os.path.join(game_dir, str(i))
        os.makedirs(run_dir, exist_ok=True)

        self.current_game_dir = game_dir
        self.current_run_dir = run_dir
        self.log_file = self._initialize_log_file(run_dir)
        return run_dir


    def _initialize_log_file(self, base_dir: str):
        """Creates a log file with a unique name based on the current timestamp in the given base_dir."""
        os.makedirs(base_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(base_dir, f"log_{timestamp}.txt")
        with open(log_file, "w") as file:
            file.write("Session Log\n")
            file.write("=" * 40 + "\n")
        return log_file

    def _write_to_log(self, content: str):
        """Appends content to the current run's log file."""
        if not self.log_file:
            # Fallback: create a default logs dir if someone calls before setup
            os.makedirs("logs", exist_ok=True)
            self.log_file = os.path.join("logs", "log_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt")
        with open(self.log_file, "a") as file:
            file.write(content + "\n")

    def _save_text(self, filename: str, text: str):
        if not self.current_run_dir:
            return
        path = os.path.join(self.current_run_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path
    
    def _exec_in_run_dir(self, code: str):
        """Run `code` with cwd set to the current run folder so any outputs
        (e.g., .efg files) are saved into that folder."""
        if not self.current_run_dir:
            raise RuntimeError("current_run_dir is not set. Did you call _ensure_dirs_for_run?")
        prev_cwd = os.getcwd()
        try:
            os.chdir(self.current_run_dir)
            exec(code, globals())
        finally:
            os.chdir(prev_cwd)


    def _save_bytes(self, filename: str, data: bytes):
        if not self.current_run_dir:
            return
        path = os.path.join(self.current_run_dir, filename)
        with open(path, "wb") as f:
            f.write(data)
        return path

    # ---------------------------
    # LLM + logging helpers
    # ---------------------------
    def get_response(self, prompt):
        """Sends a prompt to the OpenAI API and retrieves the response."""
        completion = self.client.chat.completions.create(
            model=self.api_model,
            messages=prompt,
            temperature=1,
            extra_headers=(
                {
                    "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
                    "X-OpenRouter-Title": os.getenv("OPENROUTER_SITE_NAME", "GameBenchmark"),
                }
                if "/" in self.api_model
                else None
            ),
        )
        response = completion.choices[0].message.content
        return response or ""

    def _read_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def _initialize_message_pool(self, system_message_content, example_content=None):
        system_message = {"role": "system", "content": system_message_content}
        message_pool = [system_message]
        if example_content:
            message_pool.append({"role": "user", "content": example_content})
        return message_pool

    def _handle_response(self, message_pool, user_content):
        user_message = {"role": "user", "content": user_content}
        message_pool.append(user_message)
        response = self.get_response(message_pool)
        message_pool.append({"role": "assistant", "content": response})
        return response

    def _debug_and_retry(self, message_pool, code, error_message):
        debug_prefix = self._read_file("Prompts/SelfDebug/bugs_prefix.txt")
        debug_suffix = self._read_file("Prompts/SelfDebug/bugs.txt")
        error_content = debug_prefix + error_message + debug_suffix
        self._write_to_log(f"Debugging Error:\n{error_message}\n")
        return self._handle_response(message_pool, error_content)


    def infer_code(self, game_description: str, game_name: str = "game", num_runs: int = 1):
        """Two-phase (imperfect info + code) generation. Repeats the pipeline num_runs times.
        Execution happens with cwd set to the current run folder so generated artifacts
        (like .efg files) are saved there. Stdout/stderr capturing removed."""
        results = []
        for _ in range(num_runs):
            self._ensure_dirs_for_run(game_name)

            example = self._read_file('Prompts/CodeGen/code_agent_init.txt')
            imperfect_system_message = self._read_file('Prompts/IIR/IIR_system.txt')
            imperfect_rules = self._read_file('Prompts/IIR/IIR_init.txt')
            imperfect_question = self._read_file('Prompts/IIR/constrains.txt')

            # Phase 1: imperfect information
            message_pool_imperfect = self._initialize_message_pool(imperfect_system_message)
            imperfect_user_content = (
                example + imperfect_rules + imperfect_question + "Game Description:\n" + game_description
            )
            imperfect_info = self._handle_response(message_pool_imperfect, imperfect_user_content)
            imperfect_info_code = extract_python_code(imperfect_info)

            # print("Inferred Imperfect Info Code:\n", imperfect_info_code)

            self._write_to_log(f"Imperfect Info Response (raw):\n{imperfect_info}\n")
            # self._save_text("imperfect_info.py", imperfect_info_code)

            # Phase 2: main code generation
            system_message = self._read_file('Prompts/CodeGen/codegen_system.txt')
            constraints = self._read_file('Prompts/CodeGen/constrains_v1.txt')
            final_string = (
                game_description
                + "\nThe CODE for representing the imperfect information of the game is as follows:\n"
                + imperfect_info_code + "\n"
                + constraints
            )

            message_pool = self._initialize_message_pool(system_message + example)
            response = self._handle_response(message_pool, final_string)
            code = extract_python_code(response)

            self._write_to_log(f"Final Response (raw):\n{response}\n")
            self._save_text("generated_code.py", code)

            success = 0
            # Keep your retry policy; no stdout/stderr buffering.
            for attempt in range(1, self.max_attempts + 2):
                try:
                    # <<< key change: run inside the run folder >>>
                    self._exec_in_run_dir(code)
                    self._write_to_log(f"Code execution successful on attempt {attempt}!\n")
                    try:
                        efg_path = find_efg_for_run(self.current_run_dir)
                        if efg_path is not None:
                            generated_path = copy_generated_efg("GameInterpreter", game_name, efg_path)
                            print(f"Evaluation copy: {generated_path}")
                        else:
                            print(f"No .efg file found for evaluation copy in {self.current_run_dir}")
                    except Exception as copy_error:
                        print(f"Could not save evaluation copy: {copy_error}")
                    print("Code generation successful!")
                    success = 1
                    break
                except Exception as e:
                    tb = traceback.format_exc()
                    self._write_to_log(f"Error during execution on attempt {attempt}: {e}\n{tb}\n")
                    print(f"Error during code execution (attempt {attempt}): {e} \n")

                    if attempt < self.max_attempts:
                        debug_resp = self._debug_and_retry(message_pool, code, str(e))
                        code = extract_python_code(debug_resp)
                        self._write_to_log(f"Debug_{attempt} Response (raw):\n{debug_resp}\n")
                        self._save_text(f"generated_code_retry_{attempt}.py", code)
                    else:
                        # Final failure: persist the last code variant too
                        self._save_text("generated_code_final_failed.py", code)

            if not success:
                self._write_to_log("Code generation failed after maximum retries.\n")
                print("Code generation failed after maximum retries.")
            results.append(success)

        return results
