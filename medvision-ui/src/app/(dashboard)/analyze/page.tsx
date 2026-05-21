"use client";

import { useState } from "react";
import { UploadZone } from "~/components/analyze/upload-zone";
import { ResultPanel } from "~/components/analyze/result-panel";
import { ApiError, useRequireAuth } from "~/context/auth-context";
import { predictionsApi, type AnalyzeResult } from "~/lib/api";

export default function AnalyzePage() {
  const { token } = useRequireAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);

  const handleFile = async (file: File) => {
    if (!token) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await predictionsApi.analyze(file, token);
      setResult(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analyze chest X-ray</h1>
        <p className="text-muted-foreground">
          AI classification · Grad-CAM · clinical interpretation · PDF report
        </p>
      </div>

      <UploadZone onFile={handleFile} disabled={loading} />

      {loading && (
        <div className="flex items-center justify-center gap-3 rounded-xl border border-border bg-muted/40 py-12">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-teal-600 border-t-transparent" />
          <span className="text-sm font-medium">Running inference & Grad-CAM...</span>
        </div>
      )}

      {error && (
        <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </p>
      )}

      {result && token && <ResultPanel result={result} token={token} />}
    </div>
  );
}
