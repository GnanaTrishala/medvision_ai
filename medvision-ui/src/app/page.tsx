"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Brain,
  FileText,
  Scan,
  Shield,
  Stethoscope,
} from "lucide-react";
import { Button } from "~/components/ui/button";
import { ThemeToggle } from "~/components/layout/theme-toggle";

const features = [
  {
    icon: Scan,
    title: "Instant X-Ray Analysis",
    desc: "Upload chest radiographs and receive AI classification in seconds.",
  },
  {
    icon: Brain,
    title: "Explainable AI",
    desc: "Grad-CAM heatmaps show exactly which regions drove the prediction.",
  },
  {
    icon: FileText,
    title: "Clinical Reports",
    desc: "Download PDF summaries with AI interpretation and confidence scores.",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    desc: "JWT authentication with per-clinician prediction history.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-600 text-white">
            <Stethoscope className="h-5 w-5" />
          </div>
          <span className="text-lg font-semibold tracking-tight">MedVision AI</span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button variant="ghost" asChild>
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild className="bg-teal-600 hover:bg-teal-700">
            <Link href="/signup">Get started</Link>
          </Button>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 pb-24 pt-12 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <p className="mb-4 inline-flex rounded-full border border-teal-500/30 bg-teal-500/10 px-4 py-1 text-sm font-medium text-teal-700 dark:text-teal-300">
            AI Healthcare · Chest X-Ray Intelligence
          </p>
          <h1 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Radiology-grade AI analysis,{" "}
            <span className="text-teal-600">built for clinicians</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            MedVision AI delivers pneumonia screening, confidence scoring,
            Grad-CAM explainability, and downloadable reports — in one modern
            platform.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Button size="lg" asChild className="bg-teal-600 hover:bg-teal-700">
              <Link href="/signup">
                Start free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">View dashboard</Link>
            </Button>
          </div>
        </motion.div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 pb-24 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
            className="rounded-2xl border border-border bg-card p-6 shadow-sm"
          >
            <f.icon className="mb-4 h-8 w-8 text-teal-600" />
            <h3 className="font-semibold">{f.title}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
          </motion.div>
        ))}
      </section>

      <footer className="border-t border-border py-8 text-center text-xs text-muted-foreground">
        For research and clinical decision support only — not FDA-cleared as a medical device.
      </footer>
    </div>
  );
}
