import { env } from "~/env";

const API = env.NEXT_PUBLIC_API_URL.endsWith("/api/v1")
  ? env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
  : `${env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")}/api/v1`;

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as { detail?: string | { msg: string }[] };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail[0]?.msg ?? res.statusText;
  } catch {
    /* ignore */
  }
  return res.statusText || "Request failed";
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string | null } = {},
): Promise<T> {
  const { token, ...init } = options;
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (!(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API}${path}`, { ...init, headers });
  if (!res.ok) throw new ApiError(await parseError(res), res.status);
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export type User = {
  id: number;
  email: string;
  full_name: string;
  role: string;
};

export type TokenResponse = { access_token: string; token_type: string };

export type ClassProbability = { label: string; confidence: number };

export type AnalyzeResult = {
  id: number;
  diagnosis: string;
  confidence: number;
  probabilities: ClassProbability[];
  ai_explanation: string;
  grad_cam_url: string | null;
  image_url: string;
  created_at: string;
};

export type PredictionSummary = {
  id: number;
  diagnosis: string;
  confidence: number;
  image_url: string;
  created_at: string;
};

export type PredictionDetail = PredictionSummary & {
  probabilities: ClassProbability[];
  ai_explanation: string;
  grad_cam_url: string | null;
  patient_note: string | null;
};

export type DashboardAnalytics = {
  total_predictions: number;
  pneumonia_count: number;
  normal_count: number;
  average_confidence: number;
  recent_predictions: PredictionSummary[];
  confidence_by_day: { date: string; average_confidence: number }[];
};

const API_ROOT = API.replace(/\/api\/v1$/, "");

export function assetUrl(path: string, token: string) {
  return `${API_ROOT}${path}?t=${Date.now()}`;
}

export function fileUrl(relative: string, token: string) {
  return `${API_ROOT}${relative}`;
}

export const authApi = {
  signup: (body: { email: string; password: string; full_name: string }) =>
    apiFetch<User>("/auth/signup", { method: "POST", body: JSON.stringify(body) }),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
  },

  me: (token: string) => apiFetch<User>("/auth/me", { token }),
};

export const predictionsApi = {
  analyze: (file: File, token: string) => {
    const form = new FormData();
    form.append("file", file);
    return apiFetch<AnalyzeResult>("/predictions/analyze", {
      method: "POST",
      body: form,
      token,
    });
  },
  history: (token: string) =>
    apiFetch<PredictionSummary[]>("/predictions/history", { token }),
  dashboard: (token: string) =>
    apiFetch<DashboardAnalytics>("/predictions/dashboard", { token }),
  detail: (id: number, token: string) =>
    apiFetch<PredictionDetail>(`/predictions/${id}`, { token }),
};

export async function downloadReport(predictionId: number, token: string) {
  const res = await fetch(`${API}/reports/${predictionId}/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new ApiError(await parseError(res), res.status);
  return res.blob();
}
