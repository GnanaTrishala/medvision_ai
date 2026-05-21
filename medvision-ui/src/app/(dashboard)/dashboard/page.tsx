"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Brain, Scan, TrendingUp } from "lucide-react";
import { ConfidenceChart } from "~/components/charts/confidence-chart";
import { DiagnosisChart } from "~/components/charts/diagnosis-chart";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { useRequireAuth } from "~/context/auth-context";
import { predictionsApi, type DashboardAnalytics } from "~/lib/api";

function StatCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 pt-6">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-teal-600/10 text-teal-600">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { token, user } = useRequireAuth();
  const [stats, setStats] = useState<DashboardAnalytics | null>(null);

  useEffect(() => {
    if (!token) return;
    predictionsApi.dashboard(token).then(setStats).catch(console.error);
  }, [token]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Welcome, {user?.full_name?.split(" ")[0] ?? "Doctor"}
        </h1>
        <p className="text-muted-foreground">
          Your AI radiology workspace — overview and recent activity
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total analyses"
          value={stats?.total_predictions ?? 0}
          icon={Scan}
        />
        <StatCard
          label="Pneumonia flagged"
          value={stats?.pneumonia_count ?? 0}
          icon={Brain}
        />
        <StatCard
          label="Normal findings"
          value={stats?.normal_count ?? 0}
          icon={TrendingUp}
        />
        <StatCard
          label="Avg confidence"
          value={
            stats
              ? `${(stats.average_confidence * 100).toFixed(1)}%`
              : "—"
          }
          icon={TrendingUp}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Diagnosis distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <DiagnosisChart
              normal={stats?.normal_count ?? 0}
              pneumonia={stats?.pneumonia_count ?? 0}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Confidence trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ConfidenceChart data={stats?.confidence_by_day ?? []} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Recent analyses</CardTitle>
          <Button variant="outline" size="sm" asChild>
            <Link href="/analyze">
              New scan <ArrowRight className="ml-1 h-3 w-3" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          {!stats?.recent_predictions?.length ? (
            <p className="text-sm text-muted-foreground">
              No analyses yet.{" "}
              <Link href="/analyze" className="text-teal-600 hover:underline">
                Upload your first X-ray
              </Link>
            </p>
          ) : (
            <div className="space-y-3">
              {stats.recent_predictions.map((p, i) => (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    href={`/reports/${p.id}`}
                    className="flex items-center justify-between rounded-lg border border-border px-4 py-3 transition-colors hover:bg-muted/50"
                  >
                    <div>
                      <p className="font-medium">
                        {p.diagnosis.replaceAll("_", " ")}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(p.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className="text-sm font-semibold text-teal-600">
                      {(p.confidence * 100).toFixed(1)}%
                    </span>
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
