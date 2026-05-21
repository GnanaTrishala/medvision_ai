import { env } from "~/env";

const API_BASE = env.NEXT_PUBLIC_API_URL.endsWith("/api/v1")
  ? env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
  : `${env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")}/api/v1`;

export async function fetchAuthenticatedImage(
  relativePath: string,
  token: string,
): Promise<string> {
  const res = await fetch(`${API_BASE}${relativePath}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to load image");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}
