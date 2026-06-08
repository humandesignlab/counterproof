export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 px-6 py-24">
      <h1 className="text-4xl font-semibold tracking-tight">Counterproof</h1>
      <p className="text-lg text-slate-300">
        The independent effective-challenge layer for AI underwriting.
      </p>
      <p className="text-sm text-slate-400">
        Demo UI scaffold. Upload, findings, citations, and the audit trail arrive in a later
        slice. Counterproof produces evidence and documentation; a human underwriter makes the
        decision.
      </p>
    </main>
  );
}
