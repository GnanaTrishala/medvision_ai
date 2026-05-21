export const LESION_DISPLAY: Record<string, string> = {
  akiec: "Actinic keratosis / IEC",
  bcc: "Basal cell carcinoma",
  bkl: "Benign keratosis",
  df: "Dermatofibroma",
  mel: "Melanoma",
  nv: "Melanocytic nevus",
  vasc: "Vascular lesion",
};

export const HIGH_RISK_DX = new Set(["mel", "bcc", "akiec"]);

export function formatLesion(dx: string) {
  const key = dx.toLowerCase();
  return LESION_DISPLAY[key] ?? dx.replaceAll("_", " ");
}
