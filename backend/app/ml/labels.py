"""HAM10000 skin lesion class labels (ImageFolder order: alphabetical)."""

HAM10000_CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

LESION_DISPLAY_NAMES: dict[str, str] = {
    "akiec": "Actinic keratosis / intraepithelial carcinoma",
    "bcc": "Basal cell carcinoma",
    "bkl": "Benign keratosis",
    "df": "Dermatofibroma",
    "mel": "Melanoma",
    "nv": "Melanocytic nevus",
    "vasc": "Vascular lesion",
}

# Dashboard API fields (preserved): high-risk vs common benign screening counts
HIGH_RISK_DX = {"mel", "bcc", "akiec"}
BENIGN_REFERENCE_DX = {"nv"}
