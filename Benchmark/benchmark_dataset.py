from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Optional, Union


@dataclass(frozen=True)
class DatasetGame:
    name: str
    description: str
    path: Path


GENERATED_DATASET_DIR = Path(__file__).resolve().parent / "Dataset_Generate"


def resolve_dataset_dir(dataset_dir: Union[str, Path], *, base_dir: Path) -> Path:
    path = Path(dataset_dir).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def load_games_from_dataset(dataset_dir: Union[str, Path], *, base_dir: Path) -> list[DatasetGame]:
    root = resolve_dataset_dir(dataset_dir, base_dir=base_dir)
    if not root.exists():
        raise FileNotFoundError(f"Dataset folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Dataset path is not a folder: {root}")

    games: list[DatasetGame] = []
    for game_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        description_path = game_dir / "description.txt"
        if not description_path.exists():
            continue

        description = description_path.read_text(encoding="utf-8").strip()
        if not description:
            print(f"[SKIP] Empty description: {description_path}")
            continue

        games.append(
            DatasetGame(
                name=game_dir.name,
                description=description,
                path=game_dir,
            )
        )

    if not games:
        raise FileNotFoundError(f"No game folders with description.txt found in: {root}")

    return games


def _next_generated_efg_path(method_name: str, game_name: str) -> Path:
    game_dir = GENERATED_DATASET_DIR / method_name / game_name
    game_dir.mkdir(parents=True, exist_ok=True)

    existing_numbers = []
    for path in game_dir.glob("*.efg"):
        try:
            existing_numbers.append(int(path.stem))
        except ValueError:
            continue

    next_number = max(existing_numbers, default=0) + 1
    return game_dir / f"{next_number}.efg"


def save_generated_efg_text(method_name: str, game_name: str, efg_text: str) -> Path:
    destination = _next_generated_efg_path(method_name, game_name)
    destination.write_text(efg_text, encoding="utf-8")
    return destination


def copy_generated_efg(method_name: str, game_name: str, source_path: Union[str, Path]) -> Path:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Generated EFG not found: {source}")

    destination = _next_generated_efg_path(method_name, game_name)
    shutil.copyfile(source, destination)
    return destination


def find_efg_for_run(run_dir: Union[str, Path]) -> Optional[Path]:
    run_path = Path(run_dir)
    preferred = run_path / "game.efg"
    if preferred.exists():
        return preferred

    efg_files = sorted(run_path.glob("*.efg"))
    return efg_files[0] if efg_files else None
