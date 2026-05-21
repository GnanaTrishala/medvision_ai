"""
Prepare HAM10000 for MedVision ImageFolder training.

Usage:
  python scripts/prepare_local_data.py --source ./data/ham10000 --output ./data/ham10000
"""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

HAM10000_CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def copy_class_images(src_class_dir: Path, dest_class_dir: Path) -> int:
    if not src_class_dir.is_dir():
        return 0
    dest_class_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in src_class_dir.iterdir():
        if path.suffix.lower() in IMAGE_EXTENSIONS and path.is_file():
            shutil.copy2(path, dest_class_dir / path.name)
            count += 1
    return count


def find_metadata_csv(source: Path) -> Path | None:
    for name in ("HAM10000_metadata.csv", "hmnist_28_28_L.csv"):
        candidate = source / name
        if candidate.is_file():
            return candidate
    return None


def find_image_dirs(source: Path) -> list[Path]:
    dirs = []
    for path in sorted(source.iterdir()):
        if path.is_dir() and (
            path.name.startswith("HAM10000_images")
            or path.name in ("images", "HAM10000_images")
        ):
            dirs.append(path)
    if (source / "HAM10000_images").is_dir():
        dirs.append(source / "HAM10000_images")
    return list(dict.fromkeys(dirs))


def resolve_image_path(image_dirs: list[Path], image_id: str) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png"):
        name = f"{image_id}{ext}"
        for img_dir in image_dirs:
            candidate = img_dir / name
            if candidate.is_file():
                return candidate
    return None


def prepare_ham10000(source: Path, output: Path, val_ratio: float = 0.2) -> None:
    """Build train/val ImageFolder from HAM10000 metadata + image folders."""
    if (source / "train").is_dir() and any((source / "train").iterdir()):
        print(f"Found existing ImageFolder at {source / 'train'} — skipping metadata split.")
        if output.resolve() != source.resolve():
            for split in ("train", "val"):
                src = source / split
                if src.is_dir():
                    for cls in src.iterdir():
                        if cls.is_dir():
                            copy_class_images(cls, output / split / cls.name)
        return

    metadata_path = find_metadata_csv(source)
    if not metadata_path:
        raise FileNotFoundError(
            f"No HAM10000_metadata.csv under {source}. "
            "Place the Kaggle HAM10000 files in data/ham10000/."
        )

    image_dirs = find_image_dirs(source)
    if not image_dirs:
        raise FileNotFoundError(
            f"No HAM10000_images* folders under {source}."
        )

    out_train = output / "train"
    out_val = output / "val"
    counts_train: dict[str, int] = dict.fromkeys(HAM10000_CLASSES, 0)
    counts_val: dict[str, int] = dict.fromkeys(HAM10000_CLASSES, 0)

    with metadata_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dx = (row.get("dx") or "").strip().lower()
            image_id = (row.get("image_id") or "").strip()
            if dx not in HAM10000_CLASSES or not image_id:
                continue

            src_img = resolve_image_path(image_dirs, image_id)
            if not src_img:
                continue

            # Deterministic split by image_id hash
            bucket = hash(image_id) % 100
            is_val = bucket < int(val_ratio * 100)
            dest_root = out_val if is_val else out_train
            dest_dir = dest_root / dx
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / src_img.name
            if not dest_file.exists():
                shutil.copy2(src_img, dest_file)

            if is_val:
                counts_val[dx] += 1
            else:
                counts_train[dx] += 1

    print(f"HAM10000 prepared under {output}")
    for dx in HAM10000_CLASSES:
        print(f"  {dx}: train={counts_train[dx]}, val={counts_val[dx]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare HAM10000 dataset folders")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/ham10000"),
        help="Path to HAM10000 root (metadata + image folders)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/ham10000"),
        help="Output root for train/ and val/ subfolders",
    )
    args = parser.parse_args()
    prepare_ham10000(args.source.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
