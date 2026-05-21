"""
Reorganize the Kaggle Chest X-Ray Pneumonia folder into MedVision's train/val layout.

Usage:
  python scripts/prepare_local_data.py --source ./chest_xray --output ./data
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

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


def prepare_from_chest_xray(source: Path, output: Path) -> None:
    """Map chest_xray/train and chest_xray/test into data/train and data/val."""
    train_src = source / "train"
    test_src = source / "test"

    if not train_src.is_dir():
        raise FileNotFoundError(
            f"Expected {train_src} (Kaggle layout: chest_xray/train/NORMAL, ...)"
        )

    out_train = output / "train"
    out_val = output / "val"

    total_train = 0
    for class_dir in sorted(train_src.iterdir()):
        if class_dir.is_dir():
            total_train += copy_class_images(class_dir, out_train / class_dir.name)

    total_val = 0
    if test_src.is_dir():
        for class_dir in sorted(test_src.iterdir()):
            if class_dir.is_dir():
                total_val += copy_class_images(class_dir, out_val / class_dir.name)

    print(f"Wrote {total_train} training images to {out_train}")
    if total_val:
        print(f"Wrote {total_val} validation images to {out_val}")
    else:
        print("No test/ folder found — training will auto-split 80/20 from train/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare MedVision dataset folders")
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to extracted chest_xray (or similar ImageFolder source)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data"),
        help="Output root (creates train/ and val/ inside)",
    )
    args = parser.parse_args()
    prepare_from_chest_xray(args.source.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
