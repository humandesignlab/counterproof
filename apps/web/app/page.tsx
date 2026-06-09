"use client";

import { useState } from "react";

import { Report } from "../components/Report";
import { verify } from "../lib/api";
import { CLEAN_SAMPLE, TAMPERED_SAMPLE, type Sample } from "../lib/samples";
import type { ChallengeReport } from "../lib/types";

export default function Home() {
  const [documentId, setDocumentId] = useState(TAMPERED_SAMPLE.documentId);
  const [text, setText] = useState(TAMPERED_SAMPLE.text);
  const [report, setReport] = useState<ChallengeReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function loadSample(sample: Sample) {
    setDocumentId(sample.documentId);
    setText(sample.text);
    setReport(null);
    setError(null);
  }

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const result = await verify([{ document_id: documentId, text }]);
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-8 px-6 py-16">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight">Counterproof</h1>
        <p className="text-slate-300">
          The independent effective-challenge layer for AI underwriting. Load a paystub, run it,
          and see what a naive single-pass read misses.
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => loadSample(CLEAN_SAMPLE)}
            className="rounded-md border border-slate-700 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-800"
          >
            Load clean sample
          </button>
          <button
            type="button"
            onClick={() => loadSample(TAMPERED_SAMPLE)}
            className="rounded-md border border-slate-700 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-800"
          >
            Load tampered sample
          </button>
        </div>

        <input
          aria-label="Document id"
          value={documentId}
          onChange={(event) => setDocumentId(event.target.value)}
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100"
        />
        <textarea
          aria-label="Document text"
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={16}
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-sm text-slate-100"
        />

        <button
          type="button"
          onClick={run}
          disabled={loading || text.trim().length === 0}
          className="self-start rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-50"
        >
          {loading ? "Running…" : "Run Counterproof"}
        </button>

        {error && (
          <p className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">
            {error}
          </p>
        )}
      </section>

      {report && <Report report={report} />}
    </main>
  );
}
