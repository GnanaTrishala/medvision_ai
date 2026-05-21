"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Download, ChevronLeft } from "lucide-react";
import { Button } from "~/components/ui/button";
import { ResultPanel } from "~/components/analyze/result-panel";
import { useRequireAuth } from "~/context/auth-context";
import { downloadReport, predictionsApi, type PredictionDetail } from "~/lib/api";
import type { AnalyzeResult } from "~/lib/api";

export default function ReportPage() {
  const params = useParams();
  const id = Number(params.id);
  const { token } = useRequireAuth();
  const [detail, setDetail] = useState<PredictionDetail | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!token || !id) return;
    predictionsApi.detail(id, token).then(setDetail).catch(console.error);
  }, [token, id]);

  const asResult: AnalyzeResult | null = detail
    ? {
        id: detail.id,
        diagnosis: detail.diagnosis,
        confidence: detail.confidence,
        probabilities: detail.probabilities,
        ai_explanation: detail.ai_explanation,
        grad_cam_url: detail.grad_cam_url,
        image_url: detail.image_url,
        created_at: detail.created_at,
      }
    : null;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/history">
            <ChevronLeft className="mr-1 h-4 w-4" /> Back to history
          </Link>
        </Button>
        {token && (
          <Button
            variant="outline"
            size="sm"
            disabled={downloading}
            onClick={async () => {
              setDownloading(true);
              try {
                const blob = await downloadReport(id, token);
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `medvision-report-${id}.pdf`;
                a.click();
                URL.revokeObjectURL(url);
              } finally {
                setDownloading(false);
              }
            }}
          >
            <Download className="mr-2 h-4 w-4" />
            PDF
          </Button>
        )}
      </div>

      {asResult && token ? (
        <ResultPanel result={asResult} token={token} />
      ) : (
        <div className="h-48 animate-pulse rounded-xl bg-muted" />
      )}
    </div>
  );
}
