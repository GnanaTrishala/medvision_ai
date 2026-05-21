import io

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

IMAGE_SIZE = 224

# ImageNet normalization (EfficientNet pretrained); RGB dermoscopy images
TRANSFORM = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


def load_image_from_bytes(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def preprocess_pil(image: Image.Image) -> torch.Tensor:
    return TRANSFORM(image).unsqueeze(0)


def preprocess_bytes(data: bytes) -> torch.Tensor:
    return preprocess_pil(load_image_from_bytes(data))


def tensor_to_heatmap_png_array(cam: np.ndarray) -> np.ndarray:
    """Normalize CAM to 0-255 uint8 RGB for overlay."""
    cam = cam - cam.min()
    if cam.max() > 0:
        cam = cam / cam.max()
    cam_uint8 = (cam * 255).astype(np.uint8)
    return np.stack([cam_uint8, cam_uint8, cam_uint8], axis=-1)
