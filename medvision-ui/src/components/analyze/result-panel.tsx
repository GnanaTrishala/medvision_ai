"use client";

import { motion } from "framer-motion";
import { Download, FileText } from "lucide-react";
import { useEffect, useState } from "react";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Progress } from "~/components/ui/progress";
import type { AnalyzeResult } from "~/lib/api";
import { downloadReport } from "~/lib/api";
import { fetchAuthenticatedImage } from "~/lib/assets";
import { formatLesion, HIGH_RISK_DX } from "~/lib/lesion-labels";

export function ResultPanel({
  result,
  token,
}: {
  result: AnalyzeResult;
  token: string;
}) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [gradUrl, setGradUrl] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const x = await fetchAuthenticatedImage(result.image_url, token);
        if (!cancelled) setImageUrl(x);
        if (result.grad_cam_url) {
          const g = await fetchAuthenticatedImage(result.grad_cam_url, token);
          if (!cancelled) setGradUrl(g);
        }
      } catch {
        /* ignore */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [result, token]);

  const isHighRisk = HIGH_RISK_DX.has(result.diagnosis.toLowerCase());

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const blob = await downloadReport(result.id, token);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `medvision-report-${result.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card className="border-teal-500/20 bg-gradient-to-br from-teal-500/5 to-transparent">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>AI Diagnosis</CardTitle>
            <p className="text-sm text-muted-foreground">
              EfficientNet-B0 · Grad-CAM explainability
            </p>
          </div>
          <Badge variant={isHighRisk ? "destructive" : "default"}>
            {formatLesion(result.diagnosis)}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="mb-2 flex justify-between text-sm">
              <span>Confidence</span>
              <span className="font-semibold">
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <Progress value={result.confidence * 100} className="h-2" />
          </div>
          {result.probabilities.map((p) => (
            <div key={p.label} className="flex justify-between text-sm text-muted-foreground">
              <span>{formatLesion(p.label)}</span>
              <span>{(p.confidence * 100).toFixed(1)}%</span>
            </div>
          ))}
          <Button onClick={handleDownload} disabled={downloading} className="w-full sm:w-auto">
            <Download className="mr-2 h-4 w-4" />
            {downloading ? "Generating PDF..." : "Download Medical Report"}
          </Button>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Dermoscopy Image</CardTitle>
          </CardHeader>
          <CardContent>
            {imageUrl ? (
              <img
                src={imageUrl}
                alt="Skin lesion"
                className="mx-auto max-h-80 rounded-lg object-contain"
              />
            ) : (
              <div className="h-48 animate-pulse rounded-lg bg-muted" />
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Grad-CAM Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            {gradUrl ? (
              <img
                src={gradUrl}
                alt="Grad-CAM"
                className="mx-auto max-h-80 rounded-lg object-contain"
              />
            ) : (
              <div className="h-48 animate-pulse rounded-lg bg-muted" />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="h-4 w-4 text-teal-600" />
            AI Medical Interpretation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
            {result.ai_explanation.split("\n").map((line, i) => (
              <p key={i} className={line.startsWith("**") ? "font-medium text-foreground" : ""}>
                {line.replace(/\*\*/g, "")}
              </p>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
