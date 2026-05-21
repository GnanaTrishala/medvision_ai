"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { useRequireAuth } from "~/context/auth-context";
import { predictionsApi, type PredictionSummary } from "~/lib/api";

export default function HistoryPage() {
  const { token } = useRequireAuth();
  const [items, setItems] = useState<PredictionSummary[]>([]);

  useEffect(() => {
    if (!token) return;
    predictionsApi.history(token).then(setItems).catch(console.error);
  }, [token]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Prediction history</h1>
        <p className="text-muted-foreground">All chest X-ray analyses for your account</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{items.length} records</CardTitle>
        </CardHeader>
        <CardContent className="divide-y divide-border p-0">
          {!items.length ? (
            <p className="p-6 text-sm text-muted-foreground">No predictions yet.</p>
          ) : (
            items.map((p) => (
              <Link
                key={p.id}
                href={`/reports/${p.id}`}
                className="flex items-center justify-between px-6 py-4 transition-colors hover:bg-muted/40"
              >
                <div>
                  <p className="font-medium">{p.diagnosis.replaceAll("_", " ")}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(p.created_at).toLocaleString()} · Report #{p.id}
                  </p>
                </div>
                <Badge
                  variant={
                    p.diagnosis.toUpperCase() === "PNEUMONIA" ? "destructive" : "secondary"
                  }
                >
                  {(p.confidence * 100).toFixed(1)}%
                </Badge>
              </Link>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
