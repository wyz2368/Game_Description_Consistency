import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmark_dataset import copy_generated_efg, find_efg_for_run, load_games_from_dataset


# ----------------------------
# Configuration
# ----------------------------

BASE_DIR = Path(__file__).resolve().parent
SERVER_SCRIPT = BASE_DIR / "server.py"

# Dataset folder: one game folder per entry, each with description.txt
DATASET_DIR = os.getenv("BENCHMARK_DATASET_DIR", str(ROOT / "Dataset"))

# Output root: one folder per game, then run_1, run_2, ...
OUTPUT_ROOT_DIR = BASE_DIR / os.getenv("BENCHMARK_OUTPUT_DIR", "Benchmark_gpt_5_mini_mcp")

MODEL_NAME = os.getenv("BENCHMARK_MODEL", "gpt-5-mini")
MAX_TOOL_ITERATIONS = 300

# Default run count for any game not explicitly listed below
DEFAULT_RUNS = int(os.getenv("BENCHMARK_RUNS", "10"))

# Per-game custom run counts, keyed by sanitized game_name
RUN_COUNTS = {
    "kuhn": 10,
    # "A_Game_of_Off_Path_Beliefs": 5,
}


# ----------------------------
# Templates
# ----------------------------

TASK_INSTRUCTIONS = """
Construct the extensive-form game tree using only the available tools.

Requirements:
- Complete the full game, not just the initial structure.
- When calling create_new_tree_game, do NOT include chance as a player.
- Use the tools step by step until the build is finished.
- Validate the final game.
- Save the file in the current working directory if possible.
- Return the validation result and the saved file path.
""".strip()

TOOL_SELECTION_RULES = """
Tool selection rules for building extensive-form games:

1. Use append_move_at_path when adding a move at exactly one decision node.

2. Use append_move_at_paths_as_infoset when the same player should move at
multiple terminal paths with the same actions, and those decision nodes
should be one infoset because the player cannot distinguish those paths.

3. Use make_infoset_from_paths only when the infoset cannot be created
directly with append_move_at_paths_as_infoset, such as when nodes were
already created separately or are already nonterminal.
""".strip()

EXAMPLES = """
Example 1: A Perfect-information game

Description:
There are two players, a Buyer and a Seller. The Buyer moves first and has two actions, Trust or Not trust. If the Buyer chooses Not trust, the game ends with payoffs (0, 0). If the Buyer chooses Trust, the Seller chooses Honor or Abuse. If Seller chooses Honor, payoffs are (1, 1). If Seller chooses Abuse, payoffs are (-1, 2).

Tool calls:
create_new_tree_game(
    game_id="buyer_seller",
    title="Buyer-Seller Trust Game",
    players=["Buyer", "Seller"],
)

append_move_at_path(
    game_id="buyer_seller",
    path=[],
    player="Buyer",
    actions=["Trust", "Not trust"],
)

set_outcome_at_path(
    game_id="buyer_seller",
    path=["Not trust"],
    payoffs=[0, 0],
    label="no_trust",
)

append_move_at_path(
    game_id="buyer_seller",
    path=["Trust"],
    player="Seller",
    actions=["Honor", "Abuse"],
)

set_outcome_at_path(
    game_id="buyer_seller",
    path=["Trust", "Honor"],
    payoffs=[1, 1],
    label="honor",
)

set_outcome_at_path(
    game_id="buyer_seller",
    path=["Trust", "Abuse"],
    payoffs=[-1, 2],
    label="abuse",
)

validate_game(game_id="buyer_seller")

Example 2: An Imperfect information game

Description:
There are two players, Alice and Bob.
There is a deck of cards, with equal numbers of King and Queen cards.
The game begins with each player putting $1 in the pot.
One card is dealt at random to Alice; Alice observes her card but Bob does not.
After Alice observes her card, she can choose either to Raise or to Fold.
If she chooses to Fold, Bob wins the pot and the game ends.
If she chooses to Raise, she adds another $1 to the pot.
Bob then chooses either to Meet or Pass.
If he chooses to Pass, Alice wins the pot and the game ends.
If he chooses to Meet, he adds another $1 to the pot.
There is then a showdown, in which Alice reveals her card.
If she has a King, then she wins the pot; if she has a Queen, then Bob wins the pot.

Tool calls:
create_new_tree_game(
    game_id="alice_bob_cards",
    title="Alice-Bob Card Game",
    players=["Alice", "Bob"],
)

append_chance_move_at_path(
    game_id="alice_bob_cards",
    path=[],
    actions=["King", "Queen"],
    probs=["1/2", "1/2"],
)

append_move_at_path(
    game_id="alice_bob_cards",
    path=["King"],
    player="Alice",
    actions=["Raise", "Fold"],
)

append_move_at_path(
    game_id="alice_bob_cards",
    path=["Queen"],
    player="Alice",
    actions=["Raise", "Fold"],
)

set_outcome_at_path(
    game_id="alice_bob_cards",
    path=["King", "Fold"],
    payoffs=[-1, 1],
    label="king_fold",
)

set_outcome_at_path(
    game_id="alice_bob_cards",
    path=["Queen", "Fold"],
    payoffs=[-1, 1],
    label="queen_fold",
)

append_move_at_paths_as_infoset(
    game_id="alice_bob_cards",
    paths=[["King", "Raise"], ["Queen", "Raise"]],
    player="Bob",
    actions=["Meet", "Pass"],
)

set_outcome_at_path(
    game_id="alice_bob_cards",
    path=["King", "Raise", "Pass"],
    payoffs=[1, -1],
    label="king_raise_pass",
)

set_outcome_at_path(
    game_id="alice_bob_cards",
    path=["Queen", "Raise", "Pass"],
    payoffs=[1, -1],
    label="queen_raise_pass",
)

set_outcome_at_path(
    game_id="alice_bob_cards",
    path=["King", "Raise", "Meet"],
    payoffs=[2, -2],
    label="king_showdown",
)

set_outcome_at_path(
    game_id="alice_bob_cards",
    path=["Queen", "Raise", "Meet"],
    payoffs=[-2, 2],
    label="queen_showdown",
)

validate_game(game_id="alice_bob_cards")

Example 3: An imperfect information game with imperfect recall

Description:
At junction X, an absent-minded driver chooses EXIT or CONTINUE. EXIT at X gives payoff 0. CONTINUE leads to junction Y. At junction Y, EXIT gives payoff 4 and CONTINUE gives payoff 1. The driver cannot distinguish X from Y and does not remember whether he has already passed one of them.

Tool calls:
create_new_tree_game(
    game_id="absent_minded_driver",
    title="Absent-Minded Driver",
    players=["Driver"],
)

append_move_at_path(
    game_id="absent_minded_driver",
    path=[],
    player="Driver",
    actions=["EXIT", "CONTINUE"],
)

set_outcome_at_path(
    game_id="absent_minded_driver",
    path=["EXIT"],
    payoffs=[0],
    label="A",
)

append_move_at_path(
    game_id="absent_minded_driver",
    path=["CONTINUE"],
    player="Driver",
    actions=["EXIT", "CONTINUE"],
)

make_infoset_from_paths(
    game_id="absent_minded_driver",
    paths=[[], ["CONTINUE"]],
)

set_outcome_at_path(
    game_id="absent_minded_driver",
    path=["CONTINUE", "EXIT"],
    payoffs=[4],
    label="B",
)

set_outcome_at_path(
    game_id="absent_minded_driver",
    path=["CONTINUE", "CONTINUE"],
    payoffs=[1],
    label="C",
)

validate_game(game_id="absent_minded_driver")
""".strip()


# ----------------------------
# Utilities
# ----------------------------

def get_provider(model_name: str) -> str:
    if model_name in {"deepseek", "deepseek-chat"}:
        return "deepseek"
    if "/" in model_name:
        return "openrouter"
    return "openai"


def ensure_api_key(model_name: str) -> str:
    provider = get_provider(model_name)
    env_var = {
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }[provider]
    api_key = os.environ.get(env_var, "").strip()
    if not api_key:
        raise RuntimeError(f"{env_var} is not set. Please export it before running this script.")
    return api_key


def sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "game"


def log_event(log_path: Path, event: str, **data: Any) -> None:
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{event}: {json.dumps(data, ensure_ascii=False, default=str)}\n")


def mcp_tool_to_responses_tool(tool: Any) -> dict[str, Any]:
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": tool.inputSchema,
    }


def mcp_tool_to_chat_tool(tool: Any) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


def build_user_input(game_description: str) -> str:
    return f"""
Game Description:
{game_description.strip()}

Task:
{TASK_INSTRUCTIONS}

Tool Selection Rules:
{TOOL_SELECTION_RULES}

Examples:
{EXAMPLES}
    """.strip()


def get_run_count(game_key: str) -> int:
    return RUN_COUNTS.get(game_key, DEFAULT_RUNS)


def collect_run_artifacts(run_dir: Path) -> dict[str, list[str]]:
    artifact_suffixes = {".efg", ".txt", ".json", ".log"}
    files = [
        str(p.name)
        for p in sorted(run_dir.iterdir())
        if p.is_file() and p.suffix.lower() in artifact_suffixes
    ]
    return {"files": files}


def extract_tool_output(mcp_result: Any) -> str:
    result_text_parts = []
    for content in getattr(mcp_result, "content", []):
        if getattr(content, "type", None) == "text":
            result_text_parts.append(content.text)
        else:
            result_text_parts.append(str(content))
    return "\n".join(result_text_parts) if result_text_parts else str(mcp_result)


def assistant_message_to_dict(message: Any) -> dict[str, Any]:
    msg: dict[str, Any] = {
        "role": "assistant",
        "content": message.content or "",
    }
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        msg["tool_calls"] = []
        for tc in tool_calls:
            msg["tool_calls"].append(
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
            )
    return msg


def build_client(model_name: str) -> OpenAI:
    provider = get_provider(model_name)
    if provider == "deepseek":
        return OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )
    if provider == "openrouter":
        return OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
        )
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# ----------------------------
# Core run logic
# ----------------------------

async def run_single_game(
    *,
    client: OpenAI,
    game_name: str,
    game_description: str,
    run_dir: Path,
    run_index: int,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)

    log_path = run_dir / "log.txt"
    final_output_path = run_dir / "final_output.txt"

    server_params = StdioServerParameters(
        command="python",
        args=[str(SERVER_SCRIPT)],
        cwd=str(run_dir),
    )

    log_event(
        log_path,
        "run_started",
        game_name=game_name,
        run_index=run_index,
        run_dir=str(run_dir),
        server_script=str(SERVER_SCRIPT),
    )

    provider = get_provider(MODEL_NAME)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            user_input = build_user_input(game_description)
            log_event(log_path, "run_started", model=MODEL_NAME, provider=provider)

            if provider == "openai":
                response_tools = [mcp_tool_to_responses_tool(t) for t in tools_result.tools]
                response = client.responses.create(
                    model=MODEL_NAME,
                    input=user_input,
                    tools=response_tools,
                    tool_choice="auto",
                )

                while True:
                    tool_outputs_for_model = []
                    function_calls = [item for item in response.output if item.type == "function_call"]

                    if not function_calls:
                        final_text = response.output_text or ""
                        final_output_path.write_text(final_text, encoding="utf-8")
                        log_event(log_path, "final_output", output=final_text)
                        break

                    for item in function_calls:
                        tool_name = item.name
                        tool_args = json.loads(item.arguments or "{}")

                        print(f"[{game_name} | run_{run_index}] Calling tool: {tool_name}({tool_args})")
                        log_event(log_path, "tool_call", name=tool_name, args=tool_args)

                        mcp_result = await session.call_tool(tool_name, tool_args)
                        tool_output = extract_tool_output(mcp_result)

                        print(f"[{game_name} | run_{run_index}] Tool result: {tool_output}")
                        log_event(log_path, "tool_result", name=tool_name, output=tool_output)

                        tool_outputs_for_model.append(
                            {
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": tool_output,
                            }
                        )

                    response = client.responses.create(
                        model=MODEL_NAME,
                        previous_response_id=response.id,
                        input=tool_outputs_for_model,
                        tools=response_tools,
                        tool_choice="auto",
                    )
            else:
                chat_tools = [mcp_tool_to_chat_tool(t) for t in tools_result.tools]
                messages: list[dict[str, Any]] = [{"role": "user", "content": user_input}]
                iterations = 0

                while iterations < MAX_TOOL_ITERATIONS:
                    iterations += 1
                    response = client.chat.completions.create(
                        model="deepseek-chat" if provider == "deepseek" else MODEL_NAME,
                        messages=messages,
                        tools=chat_tools,
                        tool_choice="auto",
                        extra_headers=(
                            {
                                "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
                                "X-OpenRouter-Title": os.getenv("OPENROUTER_SITE_NAME", "ExtensiveFormBenchmark"),
                            }
                            if provider == "openrouter"
                            else None
                        ),
                    )

                    message = response.choices[0].message
                    messages.append(assistant_message_to_dict(message))
                    tool_calls = getattr(message, "tool_calls", None) or []

                    if not tool_calls:
                        final_text = message.content or ""
                        final_output_path.write_text(final_text, encoding="utf-8")
                        log_event(log_path, "final_output", output=final_text, iterations=iterations)
                        break

                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments or "{}")

                        print(f"[{game_name} | run_{run_index}] Calling tool: {tool_name}({tool_args})")
                        log_event(log_path, "tool_call", name=tool_name, args=tool_args, iteration=iterations)

                        mcp_result = await session.call_tool(tool_name, tool_args)
                        tool_output = extract_tool_output(mcp_result)

                        print(f"[{game_name} | run_{run_index}] Tool result: {tool_output}")
                        log_event(log_path, "tool_result", name=tool_name, output=tool_output, iteration=iterations)

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": tool_output,
                            }
                        )
                else:
                    warning_text = f"Warning: Maximum tool iterations ({MAX_TOOL_ITERATIONS}) reached."
                    final_output_path.write_text(warning_text, encoding="utf-8")
                    log_event(log_path, "max_iterations_reached", iterations=MAX_TOOL_ITERATIONS)

    artifacts = collect_run_artifacts(run_dir)
    final_text = final_output_path.read_text(encoding="utf-8") if final_output_path.exists() else ""

    summary = {
        "game_name": game_name,
        "run_index": run_index,
        "run_dir": str(run_dir),
        "log_path": str(log_path),
        "final_output_path": str(final_output_path),
        "artifacts": artifacts,
        "final_output": final_text,
    }

    summary_path = run_dir / "run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return summary


async def run_all_games() -> None:
    ensure_api_key(MODEL_NAME)

    if not SERVER_SCRIPT.exists():
        raise FileNotFoundError(f"server.py not found: {SERVER_SCRIPT}")

    games = load_games_from_dataset(DATASET_DIR, base_dir=BASE_DIR)

    OUTPUT_ROOT_DIR.mkdir(parents=True, exist_ok=True)

    client = build_client(MODEL_NAME)
    all_results: list[dict[str, Any]] = []

    print(f"Number of games: {len(games)}")

    for game in games:
        raw_game_name = game.name
        game_description = game.description
        game_name = sanitize_name(raw_game_name)
        folder_name = game_name
        game_dir = OUTPUT_ROOT_DIR / folder_name
        game_dir.mkdir(parents=True, exist_ok=True)

        metadata_path = game_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "game_name": raw_game_name,
                    "dataset_path": str(game.path),
                    "description_path": str(game.path / "description.txt"),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        runs = get_run_count(game_name)

        print(f"\n=== Game: {raw_game_name} | runs={runs} ===")

        for run_index in range(1, runs + 1):
            run_dir = game_dir / f"run_{run_index}"
            run_dir.mkdir(parents=True, exist_ok=True)

            result = await run_single_game(
                client=client,
                game_name=game_name,
                game_description=game_description,
                run_dir=run_dir,
                run_index=run_index,
            )
            efg_path = find_efg_for_run(run_dir)
            if efg_path is not None:
                try:
                    generated_path = copy_generated_efg("MCP", raw_game_name, efg_path)
                    print(f"[{game_name} | run_{run_index}] Evaluation copy: {generated_path}")
                except Exception as copy_error:
                    print(f"[{game_name} | run_{run_index}] Could not save evaluation copy: {copy_error}")
            else:
                print(f"[{game_name} | run_{run_index}] No .efg file found for evaluation copy.")
            all_results.append(result)

    master_summary_path = OUTPUT_ROOT_DIR / "all_runs_summary.json"
    master_summary_path.write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nDone. Summary written to: {master_summary_path}")


if __name__ == "__main__":
    asyncio.run(run_all_games())
