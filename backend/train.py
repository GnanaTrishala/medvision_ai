"""
Train EfficientNet-B0 on Chest X-Ray Pneumonia dataset (ImageFolder layout).

Usage (from backend/):
  python train.py --data ../data
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import OneCycleLR
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm

from app.ml.model_loader import build_efficientnet

IMAGE_SIZE = 224


def get_transforms():
    train_t = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.Grayscale(num_output_channels=3),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(8),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )
    val_t = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )
    return train_t, val_t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("../data"))
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--output", type=Path, default=Path("models/best_model.pth"))
    args = parser.parse_args()

    train_dir = args.data / "train"
    val_dir = args.data / "val"
    if not train_dir.is_dir():
        raise FileNotFoundError(f"Missing {train_dir}. Run scripts/prepare_local_data.py first.")

    train_t, val_t = get_transforms()
    train_base = datasets.ImageFolder(train_dir, transform=train_t)
    classes = train_base.classes

    if val_dir.is_dir():
        train_ds = train_base
        val_ds = datasets.ImageFolder(val_dir, transform=val_t)
    else:
        val_base = datasets.ImageFolder(train_dir, transform=val_t)
        n = len(train_base)
        n_train = int(0.8 * n)
        n_val = n - n_train
        train_subset, val_subset = torch.utils.data.random_split(
            train_base,
            [n_train, n_val],
            generator=torch.Generator().manual_seed(42),
        )
        train_ds = train_subset
        val_ds = torch.utils.data.Subset(val_base, val_subset.indices)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_efficientnet(len(classes)).to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
    optimizer = optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    scheduler = OneCycleLR(
        optimizer,
        max_lr=1e-3,
        epochs=args.epochs,
        steps_per_epoch=len(train_loader),
    )

    best_acc = 0.0
    args.output.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        running = 0.0
        for images, labels in tqdm(train_loader, desc=f"Epoch {epoch + 1}"):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            scheduler.step()
            running += loss.item()

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                preds = model(images).argmax(1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        acc = 100 * correct / total if total else 0
        print(f"Epoch {epoch + 1} loss={running / len(train_loader):.4f} val_acc={acc:.2f}%")

        if acc > best_acc:
            best_acc = acc
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "classes": classes,
                    "accuracy": acc,
                    "epoch": epoch,
                },
                args.output,
            )
            print(f"  Saved checkpoint ({acc:.2f}%)")


if __name__ == "__main__":
    main()
