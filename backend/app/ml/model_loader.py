from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models

from app.core.config import get_settings
from app.ml.labels import HAM10000_CLASSES

DEFAULT_CLASSES = HAM10000_CLASSES


def build_efficientnet(num_classes: int = len(DEFAULT_CLASSES)) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1
    model = models.efficientnet_b0(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


class ModelBundle:
    def __init__(self):
        self.model: nn.Module | None = None
        self.classes: list[str] = list(DEFAULT_CLASSES)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._target_layer: nn.Module | None = None

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    @property
    def target_layer(self) -> nn.Module:
        if self.model is None or self._target_layer is None:
            raise RuntimeError("Model not loaded")
        return self._target_layer

    def load(self) -> None:
        settings = get_settings()
        path = Path(settings.model_path)
        self.model = build_efficientnet(len(DEFAULT_CLASSES))

        if path.is_file():
            checkpoint = torch.load(path, map_location=self.device, weights_only=False)
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.classes = checkpoint.get("classes", DEFAULT_CLASSES)
            else:
                self.model.load_state_dict(checkpoint)
        else:
            pass

        self.model.to(self.device)
        self.model.eval()
        features = self.model.features
        self._target_layer = features[-1]


bundle = ModelBundle()
