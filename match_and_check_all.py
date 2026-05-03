import argparse
import json
import os
import re
import traceback
from typing import Any, Dict, List, Optional

import yaml


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


def load_metadata(metadata_path: str) -> dict:
    with open(metadata_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_constraint_type(json_path: str):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("Cst Type")


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
    if not os.path.isdir(constraints_dir):
        return []

    json_files = []

    for filename in os.listdir(constraints_dir):
        if filename.endswith(".json"):
            json_files.append(os.path.join(constraints_dir, filename))

    json_files.sort(key=natural_sort_key)
    return json_files


def list_generation_files(generated_game_path: str, num_generations: Optional[int]):
    filenames = [
        filename
        for filename in os.listdir(generated_game_path)
        if filename.endswith(".efg")
    ]
    filenames.sort(key=natural_sort_key)

    if num_generations is not None:
        filenames = filenames[:num_generations]

    return filenames


def run_equivalence_check(
    strategic_equivalence_notion: str,
    reference_game,
    generated_game,
):
    from Algorithms import (
        check_order_preserving_equivalence,
        check_strong_vnm_equivalence,
    )

    if strategic_equivalence_notion == "Strong VNM Equivalence":
        return check_strong_vnm_equivalence(reference_game, generated_game)

    if strategic_equivalence_notion == "Order-preserving Equivalence" or "Order-Preserving Equivalence":
        return check_order_preserving_equivalence(reference_game, generated_game)

    raise ValueError(
        f"Unsupported strategic_equivalence_notion: "
        f"{strategic_equivalence_notion}"
    )


def run_constraint_check(gen_efg_path: str, json_path: str):
    from Constraints_Checker import check_efg_json, check_payoff_relation

    cst_type = load_constraint_type(json_path)

    if cst_type == 1:
        return check_efg_json(gen_efg_path, json_file=json_path)

    if cst_type == 3:
        return check_payoff_relation(gen_efg_path, json_file=json_path)

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

    if not result.get("equivalence_passed", False):
        errors.append(
            "Strategic equivalence failed: "
            f"{repr(result.get('equivalence_result'))}"
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


def write_sample_report(report_path: str, result: Dict[str, Any]):
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(f"Game: {result.get('game_name')}\n")
        file.write(f"Generated file: {result.get('generated_filename')}\n")
        file.write(f"Reference path: {result.get('ref_path')}\n")
        file.write(f"Original generated path: {result.get('generated_path')}\n")
        file.write(f"Matched path: {result.get('matched_path')}\n")
        file.write(f"Metadata path: {result.get('metadata_path')}\n")
        file.write(f"Status: {result.get('status')}\n")
        file.write("\n")

        if result.get("stage") == "match":
            file.write("=== Match Error ===\n")
            error = result.get("error", {})
            file.write(f"Type: {error.get('type')}\n")
            file.write(f"Message: {error.get('message')}\n")
            file.write("\nTraceback:\n")
            file.write(error.get("traceback", ""))
            return

        if result.get("stage") == "check_error":
            file.write("=== Check Error ===\n")
            error = result.get("error", {})
            file.write(f"Type: {error.get('type')}\n")
            file.write(f"Message: {error.get('message')}\n")
            file.write("\nTraceback:\n")
            file.write(error.get("traceback", ""))
            return

        file.write("=== Strategic Equivalence Check ===\n")
        file.write(
            "Strategic equivalence notion: "
            f"{result.get('strategic_equivalence_notion')}\n"
        )
        file.write(f"Passed: {result.get('equivalence_passed')}\n")
        file.write(f"Raw result: {repr(result.get('equivalence_result'))}\n")
        file.write("\n")

        file.write("=== Constraint Checks ===\n")
        constraint_results = result.get("constraint_results", [])

        if len(constraint_results) == 0:
            file.write("No constraint JSON files found.\n")
        else:
            for item in constraint_results:
                file.write(f"Constraint file: {item['constraint_file']}\n")
                file.write(f"Cst Type: {item['cst_type']}\n")
                file.write(f"Skipped: {item['skipped']}\n")
                file.write(f"Passed: {item['passed']}\n")
                file.write(f"Raw result: {repr(item['raw_result'])}\n")
                file.write("\n")

        file.write("=== Errors ===\n")
        errors = result.get("errors", [])
        if errors:
            for error in errors:
                file.write(f"- {error}\n")
        else:
            file.write("None\n")

        file.write("\n=== Final Result ===\n")
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
    constraints = get_constraint_json_files(constraints_dir)

    if len(constraints) == 0:
        print(f"[Warning] No constraint JSON files found for: {game_name}")

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
    from utils import get_payoff_gambit

    ref_path = os.path.join(dataset_game_path, "game.efg")
    metadata_path = os.path.join(dataset_game_path, "metadata.yml")
    constraints_dir = find_constraints_dir(dataset_game_path)

    if not os.path.exists(ref_path):
        raise FileNotFoundError(f"Reference game.efg not found: {ref_path}")

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"metadata.yml not found: {metadata_path}")

    metadata = load_metadata(metadata_path)
    strategic_equivalence_notion = metadata.get("strategic_equivalence_notion")

    if strategic_equivalence_notion is None:
        raise ValueError(
            f"strategic_equivalence_notion not found in metadata: {metadata_path}"
        )

    reference_game = get_payoff_gambit(ref_path)
    generated_game = get_payoff_gambit(matched_path)

    equivalence_result = run_equivalence_check(
        strategic_equivalence_notion=strategic_equivalence_notion,
        reference_game=reference_game,
        generated_game=generated_game,
    )
    equivalence_passed = normalize_result(equivalence_result)

    constraint_results = []

    for json_path in get_constraint_json_files(constraints_dir):
        cst_type = load_constraint_type(json_path)

        if cst_type not in {1, 3}:
            constraint_results.append(
                {
                    "constraint_file": json_path,
                    "cst_type": cst_type,
                    "skipped": True,
                    "passed": True,
                    "raw_result": f"Skipped unsupported Cst Type: {cst_type}",
                }
            )
            continue

        result = run_constraint_check(matched_path, json_path)
        passed = normalize_result(result)

        constraint_results.append(
            {
                "constraint_file": json_path,
                "cst_type": cst_type,
                "skipped": False,
                "passed": passed,
                "raw_result": result,
            }
        )

    constraints_passed = all(item["passed"] for item in constraint_results)
    all_passed = equivalence_passed and constraints_passed

    result = {
        "game_name": game_name,
        "generated_filename": generated_filename,
        "matched_path": matched_path,
        "ref_path": ref_path,
        "metadata_path": metadata_path,
        "stage": "check",
        "status": "PASS" if all_passed else "FAIL",
        "strategic_equivalence_notion": strategic_equivalence_notion,
        "equivalence_result": equivalence_result,
        "equivalence_passed": equivalence_passed,
        "constraint_results": constraint_results,
        "constraints_passed": constraints_passed,
        "all_passed": all_passed,
    }
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
    metadata_path: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "game_name": game_name,
        "generated_filename": generated_filename,
        "generated_path": generated_path,
        "matched_path": matched_path,
        "ref_path": ref_path,
        "metadata_path": metadata_path,
        "stage": stage,
        "status": "ERROR",
        "all_passed": False,
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
            "samples": [],
        },
    )

    stats["total"] += 1
    stats["samples"].append(result)

    if result.get("all_passed"):
        stats["passed"] += 1
    else:
        stats["failed"] += 1


def write_final_summary(
    summary_path: str,
    per_game_stats: Dict[str, Dict[str, Any]],
    num_generations: Optional[int],
):
    pass_label = f"pass@{num_generations}" if num_generations is not None else "pass@all"
    total_samples = sum(stats["total"] for stats in per_game_stats.values())
    total_passed = sum(stats["passed"] for stats in per_game_stats.values())
    total_failed = sum(stats["failed"] for stats in per_game_stats.values())
    total_games = len(per_game_stats)
    games_with_pass = sum(
        1 for stats in per_game_stats.values() if stats["passed"] > 0
    )
    pass_at_n = games_with_pass / total_games if total_games > 0 else None

    os.makedirs(os.path.dirname(summary_path), exist_ok=True)

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

        if pass_at_n is None:
            file.write(f"{pass_label}: N/A\n")
        else:
            file.write(f"{pass_label}: {pass_at_n:.4f}\n")
            file.write(
                f"Games with at least one passed sample: "
                f"{games_with_pass}/{total_games}\n"
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
                f"  {pass_label}: {1 if game_passed > 0 else 0}\n"
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
    pass_label = f"pass@{num_generations}" if num_generations is not None else "pass@all"
    total_samples = sum(stats["total"] for stats in per_game_stats.values())
    total_passed = sum(stats["passed"] for stats in per_game_stats.values())
    total_games = len(per_game_stats)
    games_with_pass = sum(
        1 for stats in per_game_stats.values() if stats["passed"] > 0
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

    if total_games > 0:
        print(f"{pass_label}: {games_with_pass / total_games:.4f}")
        print(f"Games with at least one passed sample: {games_with_pass}/{total_games}")
    else:
        print(f"{pass_label}: N/A")

    print("\n=== Per-Game Summary ===")

    for game_name in sorted(per_game_stats.keys(), key=natural_sort_key):
        stats = per_game_stats[game_name]
        print(
            f"{game_name}: "
            f"{stats['passed']}/{stats['total']} samples passed"
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
        help="Root folder containing reference games, descriptions, and constraints.",
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
        required=True,
        help=(
            "Number of generated samples to evaluate per game for pass@N. "
            "Required for pass@N."
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

    for generated_game_name in sorted(os.listdir(args.generated_root), key=natural_sort_key):
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
        filenames = list_generation_files(generated_game_path, args.num_generations)

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
            metadata_path = os.path.join(dataset_game_path, "metadata.yml")

            print(f"Processing: {generated_game_name}/{filename}")

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
                result = build_error_result(
                    game_name=dataset_game_name,
                    generated_filename=filename,
                    stage="match",
                    exc=exc,
                    generated_path=generated_path,
                    matched_path=matched_path,
                    ref_path=ref_path,
                    metadata_path=metadata_path,
                )
                write_sample_report(report_path, result)
                update_stats(per_game_stats, result)
                print(
                    f"[MATCH ERROR] {dataset_game_name}/{filename}: "
                    f"{type(exc).__name__}: {exc}"
                )
                continue

            try:
                result = check_one_matched_efg(
                    game_name=dataset_game_name,
                    generated_filename=filename,
                    dataset_game_path=dataset_game_path,
                    matched_path=match_result["matched_path"],
                )
                result["generated_path"] = match_result["generated_path"]
            except Exception as exc:
                result = build_error_result(
                    game_name=dataset_game_name,
                    generated_filename=filename,
                    stage="check_error",
                    exc=exc,
                    generated_path=generated_path,
                    matched_path=matched_path,
                    ref_path=ref_path,
                    metadata_path=metadata_path,
                )
                print(
                    f"[CHECK ERROR] {dataset_game_name}/{filename}: "
                    f"{type(exc).__name__}: {exc}"
                )
            else:
                if result["all_passed"]:
                    print(f"[PASS] {dataset_game_name}/{filename}")
                else:
                    print(f"[FAIL] {dataset_game_name}/{filename}")

            write_sample_report(report_path, result)
            update_stats(per_game_stats, result)

    summary_path = os.path.join(args.report_root, "summary.txt")
    write_final_summary(summary_path, per_game_stats, args.num_generations)
    print_final_summary(per_game_stats, args.num_generations, summary_path)


if __name__ == "__main__":
    main()
