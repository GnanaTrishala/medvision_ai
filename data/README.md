# HAM10000 dataset layout

MedVision uses the [HAM10000](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000) skin lesion dataset.

## Source files (under `data/ham10000/`)

```
data/ham10000/
  HAM10000_metadata.csv
  HAM10000_images/          # or HAM10000_images_part_1, part_2, etc.
```

## Class labels (7)

| Code | Lesion type |
|------|-------------|
| akiec | Actinic keratosis / intraepithelial carcinoma |
| bcc | Basal cell carcinoma |
| bkl | Benign keratosis |
| df | Dermatofibroma |
| mel | Melanoma |
| nv | Melanocytic nevus |
| vasc | Vascular lesion |

## Prepare ImageFolder layout

```bash
python scripts/prepare_local_data.py --source ./data/ham10000 --output ./data/ham10000
```

Creates:

```
data/ham10000/
  train/
    akiec/
    bcc/
    ...
  val/
    akiec/
    ...
```

## Train

```bash
cd backend
python train.py --data ../data/ham10000 --epochs 15
```
