"use client";

import { useEffect, useRef, useState } from "react";

import { Report } from "../components/Report";
import { verify, warmup } from "../lib/api";
import { CLEAN_SAMPLE, TAMPERED_SAMPLE, type Sample } from "../lib/samples";
import type { ChallengeReport } from "../lib/types";

const COLD_START_HINT_MS = 1200;

export default function Home() {
  const [documentId, setDocumentId] = useState(TAMPERED_SAMPLE.documentId);
  const [text, setText] = useState(TAMPERED_SAMPLE.text);
  const [report, setReport] = useState<ChallengeReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [slow, setSlow] = useState(false);
  const slowTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reportRef = useRef<HTMLDivElement>(null);

  // Wake the scale-to-zero API while the visitor reads the intro.
  useEffect(() => {
    void warmup();
  }, []);

  // Bring the verdict into view when a report lands, so the payoff is what the
  // visitor sees next instead of leaving it below the fold. Respect reduced motion.
  useEffect(() => {
    if (!report) return;
    const element = reportRef.current;
    if (!element || typeof element.scrollIntoView !== "function") return;
    const prefersReducedMotion =
      typeof window !== "undefined" && typeof window.matchMedia === "function"
        ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
        : false;
    element.scrollIntoView({ behavior: prefersReducedMotion ? "auto" : "smooth", block: "start" });
  }, [report]);

  function loadSample(sample: Sample) {
    setDocumentId(sample.documentId);
    setText(sample.text);
    setReport(null);
    setError(null);
  }

  async function run() {
    setLoading(true);
    setError(null);
    setSlow(false);
    slowTimer.current = setTimeout(() => setSlow(true), COLD_START_HINT_MS);
    try {
      const result = await verify([{ document_id: documentId, text }]);
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      if (slowTimer.current) clearTimeout(slowTimer.current);
      setSlow(false);
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-12 px-6 py-16 sm:py-20">
      <header className="flex flex-col gap-3">
        <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-ink-faint">
          Effective-challenge layer
        </p>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">Counterproof</h1>
        <p className="max-w-prose text-sm leading-relaxed text-ink-muted">
          An independent verification layer for AI underwriting. Load a paystub, run it, and see
          what a naive single-pass read misses.
        </p>
      </header>

      <section className="flex flex-col gap-4 border border-line bg-surface p-5" aria-label="Input">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => loadSample(CLEAN_SAMPLE)}
            className="rounded-sm border border-line px-3 py-1.5 text-sm text-ink-muted transition-colors hover:border-ink-faint hover:text-ink"
          >
            Load clean sample
          </button>
          <button
            type="button"
            onClick={() => loadSample(TAMPERED_SAMPLE)}
            className="rounded-sm border border-line px-3 py-1.5 text-sm text-ink-muted transition-colors hover:border-ink-faint hover:text-ink"
          >
            Load tampered sample
          </button>
        </div>

        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="document-id"
            className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink-faint"
          >
            Document ID
          </label>
          <input
            id="document-id"
            value={documentId}
            onChange={(event) => setDocumentId(event.target.value)}
            className="rounded-sm border border-line bg-canvas px-3 py-2 font-mono text-[13px] text-ink"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="document-text"
            className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink-faint"
          >
            Document
          </label>
          <textarea
            id="document-text"
            value={text}
            onChange={(event) => setText(event.target.value)}
            rows={16}
            className="resize-y rounded-sm border border-line bg-canvas px-3 py-2 font-mono text-[13px] leading-relaxed text-ink"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={run}
            disabled={loading || text.trim().length === 0}
            aria-busy={loading}
            className="rounded-sm bg-accent px-4 py-2 text-sm font-medium text-accent-fg transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Verifying" : "Run Counterproof"}
          </button>
          {slow && (
            <span className="text-xs text-ink-faint">
              Waking the verifier. The first run after idle can take a few seconds.
            </span>
          )}
        </div>

        {error && (
          <p
            role="alert"
            className="border-l-2 border-fail-line bg-fail-bg px-4 py-3 text-sm text-fail"
          >
            {error}
          </p>
        )}
      </section>

      {report && (
        <div ref={reportRef} className="scroll-mt-8">
          <Report report={report} />
        </div>
      )}
    </main>
  );
}
