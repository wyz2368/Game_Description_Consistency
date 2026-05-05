import argparse
import json
import os
import re
import time
import traceback
from typing import Any, Dict, List, Optional


def normalize_game_name(name: str) -> str:
    """
    Normalize game folder names for matching.

    Examples:
    1_Kuhn_Poker_V1__Single_Chance_Node
    -> kuhnpokerv1singlechancenode

    Kuhn_Poker_V1_(Single_Chance_Node)
    -> kuhnpokerv1singlechancenode
    """
    name = re.sub(r"^\d+[_-]+", "", name)
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "", name)
    return name


def natural_sort_key(value: str):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def build_dataset_lookup(dataset_root: str) -> Dict[str, str]:
    lookup = {}

    for dataset_game_name in os.listdir(dataset_root):
        dataset_game_path = os.path.join(dataset_root, dataset_game_name)

        if not os.path.isdir(dataset_game_path):
            continue

        normalized_name = normalize_game_name(dataset_game_name)

        if normalized_name in lookup:
            print(
                f"[Warning] Duplicate normalized dataset name: {normalized_name}. "
                f"Keeping {lookup[normalized_name]}, ignoring {dataset_game_name}"
            )
            continue

        lookup[normalized_name] = dataset_game_name

    return lookup


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_constraint_type(json_path: str):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("Cst Type")


def load_metadata_additional_data(metadata_path: str) -> Optional[str]:
    """
    Read metadata.yml and return the additional_data entry.

    Expected values:
    - Total Order
    - Identical Payoffs
    """
    if not os.path.exists(metadata_path):
        return None

    try:
        import yaml

        with open(metadata_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

        value = data.get("additional_data")

        if value is None:
            return None

        return str(value).strip()

    except ImportError:
        # Fallback for simple metadata.yml files like:
        # additional_data: Total Order
        with open(metadata_path, "r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()

                if stripped.startswith("additional_data:"):
                    return stripped.split(":", 1)[1].strip().strip("'\"")

    return None


def normalize_result(result) -> bool:
    if isinstance(result, bool):
        return result

    if isinstance(result, str):
        lowered = result.strip().lower()

        if lowered in {"true", "pass", "passed", "success", "successful"}:
            return True

        if lowered in {"false", "fail", "failed", "failure", "unsuccessful"}:
            return False

    if isinstance(result, dict):
        for key in ["passed", "pass", "success", "result"]:
            if key in result:
                return normalize_result(result[key])

        if result.get("skipped"):
            return True

    return bool(result)


def find_constraints_dir(dataset_game_path: str) -> str:
    candidates = [
        os.path.join(dataset_game_path, "constraints"),
        os.path.join(dataset_game_path, "Constraints"),
    ]

    for path in candidates:
        if os.path.isdir(path):
            return path

    return candidates[0]


def get_constraint_json_files(constraints_dir: str):
    """
    Return all constraint JSON files if a constraints folder exists.

    If there is no constraints folder, return [].
    This is valid because some games have no constraints.
    """
    if not os.path.isdir(constraints_dir):
        return []

    json_files = []

    for filename in os.listdir(constraints_dir):
        if filename.endswith(".json"):
            json_files.append(os.path.join(constraints_dir, filename))

    json_files.sort(key=natural_sort_key)
    return json_files


def list_generation_files(
    generated_game_path: str,
    num_generations: Optional[int],
):
    filenames = [
        filename
        for filename in os.listdir(generated_game_path)
        if filename.endswith(".efg")
    ]
    filenames.sort(key=natural_sort_key)

    if num_generations is not None:
        filenames = filenames[:num_generations]

    return filenames


def run_constraint_check(
    input_efg_path: str,
    json_path: str,
):
    """
    Run one final JSON constraint check.

    Current behavior:
    - Only Cst Type == 1 is checked at this final stage.
    - Uses Constraints_Checker.check_efg_json(candidate_efg, json_file).
    """
    from Constraints_Checker import check_efg_json

    cst_type = load_constraint_type(json_path)

    if cst_type == 1:
        return check_efg_json(input_efg_path, json_path)

    return {
        "skipped": True,
        "reason": f"Unsupported Cst Type: {cst_type}",
    }


def format_exception(exc: Exception) -> Dict[str, str]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    }


def summarize_check_failure(result: Dict[str, Any]) -> List[str]:
    errors = []

    for item in result.get("algorithm_results", []):
        if not item.get("passed", False):
            errors.append(
                "Algorithm check failed: "
                f"{item.get('check_name')} | "
                f"{repr(item.get('raw_result'))}"
            )

    for item in result.get("constraint_results", []):
        if not item.get("passed", False):
            errors.append(
                "Constraint failed: "
                f"{item.get('constraint_file')} | "
                f"Cst Type={item.get('cst_type')} | "
                f"{repr(item.get('raw_result'))}"
            )

    return errors


def ensure_parent_dir(path: str):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def write_sample_report(report_path: str, result: Dict[str, Any]):
    ensure_parent_dir(report_path)

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(f"Game: {result.get('game_name')}\n")
        file.write(f"Generated file: {result.get('generated_filename')}\n")
        file.write(f"Reference path: {result.get('ref_path')}\n")
        file.write(f"Original generated path: {result.get('generated_path')}\n")
        file.write(f"Matched path: {result.get('matched_path')}\n")
        file.write(f"Status: {result.get('status')}\n")
        file.write("\n")

        file.write("=== Timing ===\n")
        file.write(
            f"Matching time seconds: "
            f"{result.get('matching_time_seconds', 0.0):.6f}\n"
        )
        file.write(
            f"Constraint check time seconds: "
            f"{result.get('constraint_time_seconds', 0.0):.6f}\n"
        )
        file.write(
            f"Total sample time seconds: "
            f"{result.get('total_time_seconds', 0.0):.6f}\n"
        )
        file.write("\n")

        if result.get("stage") == "match":
            file.write("=== Match Error ===\n")
            error = result.get("error", {})
            file.write(f"Type: {error.get('type')}\n")
            file.write(f"Message: {error.get('message')}\n")
            file.write("\nTraceback:\n")
            file.write(error.get("traceback", ""))
            return

        if result.get("stage") == "constraint_error":
            file.write("=== Constraint Check Error ===\n")
            error = result.get("error", {})
            file.write(f"Type: {error.get('type')}\n")
            file.write(f"Message: {error.get('message')}\n")
            file.write("\nTraceback:\n")
            file.write(error.get("traceback", ""))
            return

        file.write("=== Algorithm Checks ===\n")
        algorithm_results = result.get("algorithm_results", [])

        if len(algorithm_results) == 0:
            file.write("No algorithm checks recorded.\n")
        else:
            for item in algorithm_results:
                file.write(f"Check name: {item.get('check_name')}\n")

                if "additional_data" in item:
                    file.write(f"Additional data: {item.get('additional_data')}\n")

                file.write(f"Passed: {item.get('passed')}\n")
                file.write(f"Raw result: {repr(item.get('raw_result'))}\n")
                file.write("\n")

        file.write("=== Constraint Checks ===\n")
        constraint_results = result.get("constraint_results", [])

        if len(constraint_results) == 0:
            file.write("No constraint JSON files found.\n")
        else:
            for item in constraint_results:
                file.write(f"Constraint file: {item.get('constraint_file')}\n")
                file.write(f"Cst Type: {item.get('cst_type')}\n")
                file.write(f"Skipped: {item.get('skipped')}\n")
                file.write(f"Passed: {item.get('passed')}\n")
                file.write(f"Raw result: {repr(item.get('raw_result'))}\n")
                file.write("\n")

        file.write("=== Errors ===\n")
        errors = result.get("errors", [])
        if errors:
            for error in errors:
                file.write(f"- {error}\n")
        else:
            file.write("None\n")

        file.write("\n=== Final Result ===\n")
        file.write(f"Algorithm checks passed: {result.get('algorithms_passed')}\n")
        file.write(f"Constraint checks passed: {result.get('constraints_passed')}\n")
        file.write(f"All checks passed: {result.get('all_passed')}\n")


def match_one_generated_efg(
    game_name: str,
    generated_filename: str,
    dataset_game_path: str,
    generated_game_path: str,
    output_game_path: str,
    model: str,
) -> Dict[str, Any]:
    from Match import build_global_action_mappings, match_player, switch_order
    from Tree import EFGParser

    ref_path = os.path.join(dataset_game_path, "game.efg")
    description_path = os.path.join(dataset_game_path, "description.txt")
    constraints_dir = find_constraints_dir(dataset_game_path)
    gen_efg_path = os.path.join(generated_game_path, generated_filename)
    output_path = os.path.join(output_game_path, generated_filename)

    if not os.path.exists(ref_path):
        raise FileNotFoundError(f"Reference game.efg not found: {ref_path}")

    if not os.path.exists(description_path):
        raise FileNotFoundError(f"description.txt not found: {description_path}")

    content = read_text_file(description_path)

    # This may be [] if there is no constraints folder.
    # That is valid.
    # If constraints exist, pass all JSON files to switch_order,
    # including type 2 constraints.
    constraints = get_constraint_json_files(constraints_dir)

    if len(constraints) == 0:
        print(f"[Info] No constraint JSON files found for: {game_name}")

    os.makedirs(output_game_path, exist_ok=True)

    parser_gen = EFGParser()
    parser_ref = EFGParser()

    gen_game = parser_gen.parse_file(gen_efg_path)
    ref_game = parser_ref.parse_file(ref_path)

    match_player(gen_game, ref_game, model)

    ref_total = ref_game.get_total_unique_actions()
    gen_total = gen_game.get_total_unique_actions()

    mappings = build_global_action_mappings(
        ref_total,
        gen_total,
        model,
        content,
    )

    switch_order(
        ref_game,
        gen_game,
        model,
        mappings,
        content,
        constraints,
    )

    parser_gen.save_to_efg(output_path)

    return {
        "game_name": game_name,
        "generated_filename": generated_filename,
        "generated_path": gen_efg_path,
        "matched_path": output_path,
        "ref_path": ref_path,
    }


def check_one_matched_efg(
    game_name: str,
    generated_filename: str,
    dataset_game_path: str,
    matched_path: str,
) -> Dict[str, Any]:
    """
    Check one matched EFG.

    Stages:
    1. same_reduced_strategies(candidate_path, ref_path)
    2. metadata.yml additional_data:
       - Total Order -> check_total_order_matching(reference_efg, candidate_efg)
       - Identical Payoffs -> check_payoffs(reference_efg, input_efg)
    3. Final constraint checker:
       - only JSON files with "Cst Type": 1
       - check_efg_json(matched_efg, json_file)
    """
    from Algorithms import (
        same_reduced_strategies,
        check_payoffs,
        check_total_order_matching,
    )
    from Constraints_Checker import check_efg_json

    ref_path = os.path.join(dataset_game_path, "game.efg")
    metadata_path = os.path.join(dataset_game_path, "metadata.yml")
    constraints_dir = find_constraints_dir(dataset_game_path)

    if not os.path.exists(ref_path):
        raise FileNotFoundError(f"Reference game.efg not found: {ref_path}")

    if not os.path.exists(matched_path):
        raise FileNotFoundError(f"Matched EFG not found: {matched_path}")

    algorithm_results = []
    constraint_results = []
    errors = []

    # ------------------------------------------------------------
    # Stage 1: reduced strategy set check
    # ------------------------------------------------------------
    raw_reduced_result = same_reduced_strategies(matched_path, ref_path)
    reduced_passed = normalize_result(raw_reduced_result)

    algorithm_results.append(
        {
            "check_name": "same_reduced_strategies",
            "passed": reduced_passed,
            "raw_result": raw_reduced_result,
        }
    )

    if not reduced_passed:
        errors.append("Reduced strategy sets don't match.")

    # ------------------------------------------------------------
    # Stage 2: metadata-driven algorithm check
    # ------------------------------------------------------------
    additional_data = load_metadata_additional_data(metadata_path)

    if additional_data is None:
        algorithm_results.append(
            {
                "check_name": "metadata_additional_data",
                "passed": False,
                "raw_result": "metadata.yml missing or additional_data not found",
            }
        )
        errors.append("metadata.yml missing or additional_data not found.")

    elif additional_data == "Total Order":
        raw_total_order_result = check_total_order_matching(
            ref_path,
            matched_path,
        )
        total_order_passed = normalize_result(raw_total_order_result)

        algorithm_results.append(
            {
                "check_name": "check_total_order_matching",
                "additional_data": additional_data,
                "passed": total_order_passed,
                "raw_result": raw_total_order_result,
            }
        )

        if not total_order_passed:
            errors.append("Total order matching failed.")

    elif additional_data == "Identical Payoffs":
        raw_payoff_result = check_payoffs(
            ref_path,
            matched_path,
        )
        payoff_passed = normalize_result(raw_payoff_result)

        algorithm_results.append(
            {
                "check_name": "check_payoffs",
                "additional_data": additional_data,
                "passed": payoff_passed,
                "raw_result": raw_payoff_result,
            }
        )

        if not payoff_passed:
            errors.append("Identical payoffs check failed.")

    else:
        algorithm_results.append(
            {
                "check_name": "metadata_additional_data",
                "passed": False,
                "raw_result": f"Unsupported additional_data: {additional_data}",
            }
        )
        errors.append(f"Unsupported additional_data value: {additional_data}")

    # ------------------------------------------------------------
    # Stage 3: final JSON constraint checker
    # Missing constraint folder is valid.
    # Only Cst Type == 1 is checked here.
    # ------------------------------------------------------------
    json_files = get_constraint_json_files(constraints_dir)

    if len(json_files) == 0:
        constraint_results.append(
            {
                "constraint_file": None,
                "cst_type": None,
                "skipped": True,
                "passed": True,
                "raw_result": "No constraint folder or no JSON constraint files found.",
            }
        )

    for json_path in json_files:
        cst_type = load_constraint_type(json_path)

        if cst_type != 1:
            constraint_results.append(
                {
                    "constraint_file": json_path,
                    "cst_type": cst_type,
                    "skipped": True,
                    "passed": True,
                    "raw_result": f"Skipped unsupported Cst Type at final stage: {cst_type}",
                }
            )
            continue

        raw_result = check_efg_json(
            matched_path,
            json_path,
        )
        passed = normalize_result(raw_result)

        constraint_results.append(
            {
                "constraint_file": json_path,
                "cst_type": cst_type,
                "skipped": False,
                "passed": passed,
                "raw_result": raw_result,
            }
        )

        if not passed:
            errors.append(
                "JSON constraint failed: "
                f"{json_path} | Cst Type={cst_type} | {repr(raw_result)}"
            )

    algorithms_passed = all(item["passed"] for item in algorithm_results)
    constraints_passed = all(item["passed"] for item in constraint_results)
    all_passed = algorithms_passed and constraints_passed

    result = {
        "game_name": game_name,
        "generated_filename": generated_filename,
        "matched_path": matched_path,
        "ref_path": ref_path,
        "stage": "final_check",
        "status": "PASS" if all_passed else "FAIL",
        "algorithm_results": algorithm_results,
        "constraint_results": constraint_results,
        "algorithms_passed": algorithms_passed,
        "constraints_passed": constraints_passed,
        "all_passed": all_passed,
        "errors": errors,
    }

    if not errors:
        result["errors"] = summarize_check_failure(result)

    return result


def build_error_result(
    game_name: str,
    generated_filename: str,
    stage: str,
    exc: Exception,
    generated_path: Optional[str] = None,
    matched_path: Optional[str] = None,
    ref_path: Optional[str] = None,
    matching_time_seconds: float = 0.0,
    constraint_time_seconds: float = 0.0,
) -> Dict[str, Any]:
    total_time_seconds = matching_time_seconds + constraint_time_seconds

    return {
        "game_name": game_name,
        "generated_filename": generated_filename,
        "generated_path": generated_path,
        "matched_path": matched_path,
        "ref_path": ref_path,
        "stage": stage,
        "status": "ERROR",
        "all_passed": False,
        "algorithms_passed": False,
        "constraints_passed": False,
        "matching_time_seconds": matching_time_seconds,
        "constraint_time_seconds": constraint_time_seconds,
        "total_time_seconds": total_time_seconds,
        "error": format_exception(exc),
        "errors": [f"{type(exc).__name__}: {exc}"],
    }


def update_stats(per_game_stats: Dict[str, Dict[str, Any]], result: Dict[str, Any]):
    game_name = result["game_name"]

    stats = per_game_stats.setdefault(
        game_name,
        {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "matching_time_seconds": 0.0,
            "constraint_time_seconds": 0.0,
            "total_time_seconds": 0.0,
            "samples": [],
        },
    )

    stats["total"] += 1
    stats["samples"].append(result)

    if result.get("all_passed"):
        stats["passed"] += 1
    else:
        stats["failed"] += 1

    stats["matching_time_seconds"] += result.get("matching_time_seconds", 0.0)
    stats["constraint_time_seconds"] += result.get("constraint_time_seconds", 0.0)
    stats["total_time_seconds"] += result.get("total_time_seconds", 0.0)


def write_final_summary(
    summary_path: str,
    per_game_stats: Dict[str, Dict[str, Any]],
    num_generations: Optional[int],
):
    total_samples = sum(stats["total"] for stats in per_game_stats.values())
    total_passed = sum(stats["passed"] for stats in per_game_stats.values())
    total_failed = sum(stats["failed"] for stats in per_game_stats.values())
    total_games = len(per_game_stats)

    total_matching_time = sum(
        stats["matching_time_seconds"] for stats in per_game_stats.values()
    )
    total_constraint_time = sum(
        stats["constraint_time_seconds"] for stats in per_game_stats.values()
    )
    total_eval_time = sum(
        stats["total_time_seconds"] for stats in per_game_stats.values()
    )

    ensure_parent_dir(summary_path)

    with open(summary_path, "w", encoding="utf-8") as file:
        file.write("=== Final Combined Summary ===\n")
        file.write(f"Requested generations per game: {num_generations or 'all'}\n")
        file.write(f"Total games evaluated: {total_games}\n")
        file.write(f"Total samples evaluated: {total_samples}\n")
        file.write(f"Total passed samples: {total_passed}\n")
        file.write(f"Total failed samples: {total_failed}\n")

        if total_samples > 0:
            file.write(f"Sample pass rate: {total_passed / total_samples:.4f}\n")
        else:
            file.write("Sample pass rate: N/A\n")

        file.write("\n=== Timing Summary ===\n")
        file.write(f"Total matching time seconds: {total_matching_time:.6f}\n")
        file.write(f"Total constraint check time seconds: {total_constraint_time:.6f}\n")
        file.write(f"Total evaluation time seconds: {total_eval_time:.6f}\n")

        if total_samples > 0:
            file.write(
                f"Average matching time per sample seconds: "
                f"{total_matching_time / total_samples:.6f}\n"
            )
            file.write(
                f"Average constraint check time per sample seconds: "
                f"{total_constraint_time / total_samples:.6f}\n"
            )
            file.write(
                f"Average total time per sample seconds: "
                f"{total_eval_time / total_samples:.6f}\n"
            )

        file.write("\n=== Per-Game Summary ===\n")

        for game_name in sorted(per_game_stats.keys(), key=natural_sort_key):
            stats = per_game_stats[game_name]
            game_total = stats["total"]
            game_passed = stats["passed"]
            game_failed = stats["failed"]
            game_pass_rate = game_passed / game_total if game_total > 0 else None

            file.write(f"{game_name}\n")
            file.write(f"  Total samples: {game_total}\n")
            file.write(f"  Passed samples: {game_passed}\n")
            file.write(f"  Failed samples: {game_failed}\n")
            file.write(
                "  Sample pass rate: "
                f"{game_pass_rate:.4f}\n" if game_pass_rate is not None else
                "  Sample pass rate: N/A\n"
            )

            file.write(
                f"  Total matching time seconds: "
                f"{stats['matching_time_seconds']:.6f}\n"
            )
            file.write(
                f"  Total constraint check time seconds: "
                f"{stats['constraint_time_seconds']:.6f}\n"
            )
            file.write(
                f"  Total game time seconds: "
                f"{stats['total_time_seconds']:.6f}\n"
            )

            if game_total > 0:
                file.write(
                    f"  Average matching time per sample seconds: "
                    f"{stats['matching_time_seconds'] / game_total:.6f}\n"
                )
                file.write(
                    f"  Average constraint check time per sample seconds: "
                    f"{stats['constraint_time_seconds'] / game_total:.6f}\n"
                )
                file.write(
                    f"  Average total time per sample seconds: "
                    f"{stats['total_time_seconds'] / game_total:.6f}\n"
                )

            file.write("  Samples:\n")

            for sample in sorted(
                stats["samples"],
                key=lambda item: natural_sort_key(item["generated_filename"]),
            ):
                file.write(
                    f"    - {sample['generated_filename']}: "
                    f"{sample.get('status')}"
                )
                file.write(
                    f" | matching={sample.get('matching_time_seconds', 0.0):.6f}s"
                )
                file.write(
                    f" | constraints={sample.get('constraint_time_seconds', 0.0):.6f}s"
                )
                file.write(
                    f" | total={sample.get('total_time_seconds', 0.0):.6f}s"
                )

                if sample.get("all_passed"):
                    file.write(" | passed\n")
                    continue

                errors = sample.get("errors") or []

                if not errors and sample.get("error"):
                    error = sample["error"]
                    errors = [f"{error.get('type')}: {error.get('message')}"]

                if errors:
                    file.write(f" | error: {'; '.join(errors)}\n")
                else:
                    file.write(" | error: checks failed\n")

            file.write("\n")


def print_final_summary(
    per_game_stats: Dict[str, Dict[str, Any]],
    num_generations: Optional[int],
    summary_path: str,
):
    total_samples = sum(stats["total"] for stats in per_game_stats.values())
    total_passed = sum(stats["passed"] for stats in per_game_stats.values())
    total_games = len(per_game_stats)

    total_matching_time = sum(
        stats["matching_time_seconds"] for stats in per_game_stats.values()
    )
    total_constraint_time = sum(
        stats["constraint_time_seconds"] for stats in per_game_stats.values()
    )
    total_eval_time = sum(
        stats["total_time_seconds"] for stats in per_game_stats.values()
    )

    print("\n=== Final Combined Summary ===")
    print(f"Requested generations per game: {num_generations or 'all'}")
    print(f"Total games evaluated: {total_games}")
    print(f"Total samples evaluated: {total_samples}")
    print(f"Total passed samples: {total_passed}")
    print(f"Total failed samples: {total_samples - total_passed}")

    if total_samples > 0:
        print(f"Sample pass rate: {total_passed / total_samples:.4f}")
    else:
        print("Sample pass rate: N/A")

    print("\n=== Timing Summary ===")
    print(f"Total matching time seconds: {total_matching_time:.6f}")
    print(f"Total constraint check time seconds: {total_constraint_time:.6f}")
    print(f"Total evaluation time seconds: {total_eval_time:.6f}")

    if total_samples > 0:
        print(
            f"Average matching time per sample seconds: "
            f"{total_matching_time / total_samples:.6f}"
        )
        print(
            f"Average constraint check time per sample seconds: "
            f"{total_constraint_time / total_samples:.6f}"
        )
        print(
            f"Average total time per sample seconds: "
            f"{total_eval_time / total_samples:.6f}"
        )

    print("\n=== Per-Game Summary ===")

    for game_name in sorted(per_game_stats.keys(), key=natural_sort_key):
        stats = per_game_stats[game_name]
        print(
            f"{game_name}: "
            f"{stats['passed']}/{stats['total']} samples passed | "
            f"matching={stats['matching_time_seconds']:.6f}s | "
            f"constraints={stats['constraint_time_seconds']:.6f}s | "
            f"total={stats['total_time_seconds']:.6f}s"
        )

    print(f"\nSummary saved to: {summary_path}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="gpt-5-mini",
        help="OpenAI model to use for matching, for example: 'gpt-5-mini'.",
    )

    parser.add_argument(
        "--dataset_root",
        type=str,
        default="Dataset",
        help="Root folder containing reference games, descriptions, metadata, and constraints.",
    )

    parser.add_argument(
        "--generated_root",
        type=str,
        default="Benchmark",
        help="Root folder containing generated game folders.",
    )

    parser.add_argument(
        "--output_root",
        type=str,
        default="Results/Output",
        help="Folder where matched EFG files will be saved.",
    )

    parser.add_argument(
        "--report_root",
        type=str,
        default="Results/Check_Reports",
        help="Folder where reports and final summary will be saved.",
    )

    parser.add_argument(
        "-n",
        "--num_generations",
        type=int,
        default=None,
        help=(
            "Optional number of generated samples to evaluate per game. "
            "If omitted, all generated .efg files are evaluated."
        ),
    )

    args = parser.parse_args()

    if args.num_generations is not None and args.num_generations <= 0:
        raise ValueError("--num_generations must be greater than 0")

    if not os.path.isdir(args.dataset_root):
        raise FileNotFoundError(f"Dataset root not found: {args.dataset_root}")

    if not os.path.isdir(args.generated_root):
        raise FileNotFoundError(f"Generated root not found: {args.generated_root}")

    dataset_lookup = build_dataset_lookup(args.dataset_root)
    per_game_stats: Dict[str, Dict[str, Any]] = {}

    for generated_game_name in sorted(
        os.listdir(args.generated_root),
        key=natural_sort_key,
    ):
        generated_game_path = os.path.join(args.generated_root, generated_game_name)

        if not os.path.isdir(generated_game_path):
            continue

        normalized_generated_name = normalize_game_name(generated_game_name)
        dataset_game_name = dataset_lookup.get(normalized_generated_name)

        if dataset_game_name is None:
            print(
                f"[Skipping] No matching dataset folder found for: "
                f"{generated_game_name}"
            )
            continue

        dataset_game_path = os.path.join(args.dataset_root, dataset_game_name)
        output_game_path = os.path.join(args.output_root, dataset_game_name)
        report_game_path = os.path.join(args.report_root, dataset_game_name)

        filenames = list_generation_files(
            generated_game_path,
            args.num_generations,
        )

        if len(filenames) == 0:
            print(f"[Skipping] No generated .efg files found for: {generated_game_name}")
            continue

        for filename in filenames:
            generated_path = os.path.join(generated_game_path, filename)
            matched_path = os.path.join(output_game_path, filename)
            report_path = os.path.join(
                report_game_path,
                os.path.splitext(filename)[0] + ".txt",
            )
            ref_path = os.path.join(dataset_game_path, "game.efg")

            print(f"Processing: {generated_game_name}/{filename}")

            matching_time_seconds = 0.0
            constraint_time_seconds = 0.0

            match_start = time.perf_counter()

            try:
                match_result = match_one_generated_efg(
                    game_name=dataset_game_name,
                    generated_filename=filename,
                    dataset_game_path=dataset_game_path,
                    generated_game_path=generated_game_path,
                    output_game_path=output_game_path,
                    model=args.model,
                )
            except Exception as exc:
                matching_time_seconds = time.perf_counter() - match_start

                result = build_error_result(
                    game_name=dataset_game_name,
                    generated_filename=filename,
                    stage="match",
                    exc=exc,
                    generated_path=generated_path,
                    matched_path=matched_path,
                    ref_path=ref_path,
                    matching_time_seconds=matching_time_seconds,
                    constraint_time_seconds=0.0,
                )

                write_sample_report(report_path, result)
                update_stats(per_game_stats, result)

                print(
                    f"[MATCH ERROR] {dataset_game_name}/{filename}: "
                    f"{type(exc).__name__}: {exc} | "
                    f"matching_time={matching_time_seconds:.6f}s"
                )
                continue

            matching_time_seconds = time.perf_counter() - match_start

            constraint_start = time.perf_counter()

            try:
                result = check_one_matched_efg(
                    game_name=dataset_game_name,
                    generated_filename=filename,
                    dataset_game_path=dataset_game_path,
                    matched_path=match_result["matched_path"],
                )
                constraint_time_seconds = time.perf_counter() - constraint_start

                result["generated_path"] = match_result["generated_path"]
                result["matching_time_seconds"] = matching_time_seconds
                result["constraint_time_seconds"] = constraint_time_seconds
                result["total_time_seconds"] = (
                    matching_time_seconds + constraint_time_seconds
                )

            except Exception as exc:
                constraint_time_seconds = time.perf_counter() - constraint_start

                result = build_error_result(
                    game_name=dataset_game_name,
                    generated_filename=filename,
                    stage="constraint_error",
                    exc=exc,
                    generated_path=generated_path,
                    matched_path=matched_path,
                    ref_path=ref_path,
                    matching_time_seconds=matching_time_seconds,
                    constraint_time_seconds=constraint_time_seconds,
                )

                print(
                    f"[CONSTRAINT ERROR] {dataset_game_name}/{filename}: "
                    f"{type(exc).__name__}: {exc} | "
                    f"matching_time={matching_time_seconds:.6f}s | "
                    f"constraint_time={constraint_time_seconds:.6f}s"
                )
            else:
                if result["all_passed"]:
                    print(
                        f"[PASS] {dataset_game_name}/{filename} | "
                        f"matching_time={matching_time_seconds:.6f}s | "
                        f"constraint_time={constraint_time_seconds:.6f}s | "
                        f"total_time={result['total_time_seconds']:.6f}s"
                    )
                else:
                    print(
                        f"[FAIL] {dataset_game_name}/{filename} | "
                        f"matching_time={matching_time_seconds:.6f}s | "
                        f"constraint_time={constraint_time_seconds:.6f}s | "
                        f"total_time={result['total_time_seconds']:.6f}s"
                    )

            write_sample_report(report_path, result)
            update_stats(per_game_stats, result)

    summary_path = os.path.join(args.report_root, "summary.txt")
    write_final_summary(summary_path, per_game_stats, args.num_generations)
    print_final_summary(per_game_stats, args.num_generations, summary_path)


if __name__ == "__main__":
    main()