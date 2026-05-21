# Medical image dataset layout

MedVision expects images organized for PyTorch `ImageFolder`:

```
data/
  train/
    NORMAL/
      img001.jpeg
      ...
    PNEUMONIA/
      img002.jpeg
      ...
  val/          # optional — if omitted, 20% of train is used for validation
    NORMAL/
    PNEUMONIA/
```

Supported formats: `.png`, `.jpg`, `.jpeg`, `.webp`

## Recommended starter dataset

**Chest X-Ray Pneumonia** (Kaggle):

- https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia

After downloading and extracting, run from the project root:

```bash
python scripts/prepare_local_data.py --source path/to/chest_xray --output data
```

## Upload to Modal for cloud training

```bash
modal volume create medical-data
modal volume put medical-data ./data/medical medical
```

This mounts at `/data/medical` inside the training container (see `train.py`).

## Class names

Folder names become labels (e.g. `NORMAL`, `PNEUMONIA`). Use clear, consistent names — they appear in the UI and API responses.
