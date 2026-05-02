import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

METHOD_SPECS = {
    "direct": {
        "script": "run_all.py",
        "cwd": "Direct_Generation",
        "supports": {"gpt-5-mini", "deepseek-chat", "qwen/qwen3.5-35b-a3b"},
        "args": lambda model, cfg: [
            "--model", model,
            "--dataset-dir", cfg["dataset_dir"],
            "--runs", str(cfg["runs"]),
        ] + (["--output-root", cfg["output_dir"]] if cfg["output_dir"] else [])
    },
    "gameinterpreter": {
        "script": None,
        "cwd": None,
        "supports": {"gpt-5-mini", "deepseek-chat", "qwen/qwen3.5-35b-a3b"},
    },
    "iterative": {
        "script": None,
        "cwd": None,
        "supports": {"gpt-5-mini", "deepseek-chat", "qwen/qwen3.5-35b-a3b"},
    },
    "mcp": {
        "script": None,
        "cwd": None,
        "supports": {"gpt-5-mini", "deepseek-chat", "qwen/qwen3.5-35b-a3b"},
    },
}

MODEL_TARGETS = {
    "gameinterpreter": {
        "gpt-5-mini": ("run_all.py", "GameInterpreter"),
        "deepseek-chat": ("run_all.py", "GameInterpreter"),
        "qwen/qwen3.5-35b-a3b": ("run_all.py", "GameInterpreter"),
    },
    "iterative": {
        "gpt-5-mini": ("main.py", "Iterative_Generation"),
        "deepseek-chat": ("main.py", "Iterative_Generation"),
        "qwen/qwen3.5-35b-a3b": ("main.py", "Iterative_Generation"),
    },
    "mcp": {
        "gpt-5-mini": ("client_main.py", "MCP_Generation"),
        "deepseek-chat": ("client_main.py", "MCP_Generation"),
        "qwen/qwen3.5-35b-a3b": ("client_main.py", "MCP_Generation"),
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run one benchmark method with one model."
    )
    parser.add_argument(
        "--method",
        required=True,
        choices=sorted(METHOD_SPECS.keys()),
        help="Benchmark method to run.",
    )
    parser.add_argument(
        "--model",
        required=True,
        choices=["gpt-5-mini", "deepseek-chat", "qwen/qwen3.5-35b-a3b"],
        help="Model to benchmark.",
    )
    parser.add_argument("--runs", type=int, default=10, help="Runs per game.")
    parser.add_argument("--dataset-dir", default="Dataset", help="Folder containing one subfolder per game.")
    parser.add_argument("--output-dir", default=None, help="Optional custom output directory name.")
    return parser.parse_args()


def resolve_target(method: str, model: str):
    if method == "direct":
        spec = METHOD_SPECS[method]
        return spec["script"], spec["cwd"]
    return MODEL_TARGETS[method][model]


def default_output_dir(method: str, model: str) -> str:
    safe_model = model.replace("/", "_").replace("-", "_")
    return f"benchmark_{method}_{safe_model}"


def ensure_api_key_for_model(model: str, env: dict[str, str]) -> None:
    if model == "gpt-5-mini" and not env.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for gpt-5-mini.")
    if model == "deepseek-chat" and not env.get("DEEPSEEK_API_KEY"):
        raise RuntimeError("DEEPSEEK_API_KEY is required for deepseek-chat.")
    if "/" in model and not env.get("OPENROUTER_API_KEY"):
        raise RuntimeError("OPENROUTER_API_KEY is required for OpenRouter models.")


def build_command(method: str, model: str, cfg: dict[str, str]):
    script, cwd = resolve_target(method, model)
    python = sys.executable
    if method == "direct":
        args = METHOD_SPECS[method]["args"](model, cfg)
    elif method == "gameinterpreter":
        args = ["-m", model]
    elif method == "iterative":
        args = ["--model", model]
    else:
        args = []
    return [python, script, *args], ROOT / cwd


def main():
    args = parse_args()
    env = os.environ.copy()
    env["BENCHMARK_MODEL"] = args.model
    env["BENCHMARK_RUNS"] = str(args.runs)
    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.is_absolute():
        dataset_dir = ROOT / dataset_dir
    env["BENCHMARK_DATASET_DIR"] = str(dataset_dir.resolve())

    env["BENCHMARK_OUTPUT_DIR"] = args.output_dir or default_output_dir(args.method, args.model)
    ensure_api_key_for_model(args.model, env)

    command, cwd = build_command(
        args.method,
        args.model,
        {
            "runs": args.runs,
            "dataset_dir": env["BENCHMARK_DATASET_DIR"],
            "output_dir": env["BENCHMARK_OUTPUT_DIR"],
        },
    )

    print(f"Running method={args.method} model={args.model}", flush=True)
    print(f"Working directory: {cwd}", flush=True)
    print(f"Dataset folder: {env['BENCHMARK_DATASET_DIR']}", flush=True)
    print(f"Output directory: {env['BENCHMARK_OUTPUT_DIR']}", flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


if __name__ == "__main__":
    main()
