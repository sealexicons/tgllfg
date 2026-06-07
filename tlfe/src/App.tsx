// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { useState, type FormEvent } from "react";
import { Tabs } from "radix-ui";

import type { ParseModel, ParseResponse } from "./api/client";
import { useParse } from "./api/hooks";
import { CStructureView } from "./views/CStructureView";
import { FStructureView } from "./views/FStructureView";

// The four LFG projections. The c-/f-/a- renderers land in 14.B.3–14.B.5;
// until then those tabs point at the JSON tab, which shows the real payload.
const VIEWS = [
  { value: "cstructure", label: "C-structure", soon: null },
  { value: "fstructure", label: "F-structure", soon: null },
  { value: "astructure", label: "A-structure", soon: "14.B.5" },
  { value: "json", label: "JSON", soon: null },
] as const;

const N_BEST = 5;

function App() {
  const [text, setText] = useState("");
  const [selectedParse, setSelectedParse] = useState(0);
  const parse = useParse();
  const result = parse.data;
  const parses = result?.parses ?? [];
  const canParse = text.trim().length > 0 && !parse.isPending;

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || parse.isPending) return;
    setSelectedParse(0);
    parse.mutate({ body: { text: trimmed, n_best: N_BEST, strict: false } });
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 px-6 py-10 text-slate-800">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">tgllfg inspector</h1>
        <p className="text-sm text-slate-500">
          Tagalog LFG parser — enter a sentence to inspect its c-, f-, and a-structures.
        </p>
      </header>

      <form onSubmit={onSubmit} className="flex items-center gap-2">
        <input
          type="text"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Bumili ng aklat ang bata."
          aria-label="Tagalog sentence"
          autoComplete="off"
          className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
        />
        <button
          type="submit"
          disabled={!canParse}
          className="rounded-md bg-violet-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {parse.isPending ? "Parsing…" : "Parse"}
        </button>
      </form>

      <StatusRegion parse={parse} />

      {parses.length > 1 && (
        <ParseSelector parses={parses} index={selectedParse} onSelect={setSelectedParse} />
      )}

      <Tabs.Root defaultValue="cstructure" className="flex flex-col gap-3">
        <Tabs.List aria-label="Parse views" className="flex gap-1 border-b border-slate-200">
          {VIEWS.map((view) => (
            <Tabs.Trigger
              key={view.value}
              value={view.value}
              className="-mb-px border-b-2 border-transparent px-3 py-2 text-sm text-slate-500 data-[state=active]:border-violet-600 data-[state=active]:text-violet-700"
            >
              {view.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        {VIEWS.map((view) => (
          <Tabs.Content
            key={view.value}
            value={view.value}
            className="rounded-md border border-slate-200 p-4 text-sm"
          >
            {view.value === "json" ? (
              <JsonView result={result} />
            ) : view.value === "cstructure" ? (
              <CStructureView result={result} selected={selectedParse} />
            ) : view.value === "fstructure" ? (
              <FStructureView result={result} selected={selectedParse} />
            ) : (
              <Placeholder label={view.label} soon={view.soon} hasResult={Boolean(result)} />
            )}
          </Tabs.Content>
        ))}
      </Tabs.Root>
    </main>
  );
}

function StatusRegion({ parse }: { parse: ReturnType<typeof useParse> }) {
  if (parse.isPending) {
    return <p className="text-sm text-slate-500">Parsing…</p>;
  }
  if (parse.isError) {
    return (
      <p
        role="alert"
        className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
      >
        Parse failed: {parse.error?.message ?? "unknown error"}
      </p>
    );
  }
  if (!parse.data) {
    return <p className="text-sm text-slate-400">Enter a Tagalog sentence and press Parse.</p>;
  }
  return <MetaBar result={parse.data} />;
}

function MetaBar({ result }: { result: ParseResponse }) {
  const { parse_count, fragment_count, n_best } = result.meta;
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
      <span className="font-medium">
        {parse_count > 0
          ? `${parse_count} complete parse${parse_count === 1 ? "" : "s"}`
          : "No complete parse"}
      </span>
      {fragment_count > 0 && (
        <span className="text-slate-500">
          {fragment_count} fragment{fragment_count === 1 ? "" : "s"}
        </span>
      )}
      <span className="text-slate-400">n_best={n_best}</span>
    </div>
  );
}

function JsonView({ result }: { result: ParseResponse | undefined }) {
  if (!result) {
    return <p className="text-slate-400">Parse a sentence to see the raw payload.</p>;
  }
  return (
    <pre className="max-h-[28rem] overflow-auto rounded bg-slate-900 p-3 text-xs leading-relaxed text-slate-100">
      {JSON.stringify(result, null, 2)}
    </pre>
  );
}

function Placeholder({
  label,
  soon,
  hasResult,
}: {
  label: string;
  soon: string | null;
  hasResult: boolean;
}) {
  return (
    <p className="text-slate-500">
      {label} renderer {soon ? `arrives in ${soon}` : "coming soon"}.
      {hasResult && " For now, the JSON tab shows the raw payload."}
    </p>
  );
}

function ParseSelector({
  parses,
  index,
  onSelect,
}: {
  parses: ParseModel[];
  index: number;
  onSelect: (next: number) => void;
}) {
  const clamped = Math.min(Math.max(index, 0), parses.length - 1);
  return (
    <label className="text-xs text-slate-500">
      Showing parse{" "}
      <select
        value={clamped}
        onChange={(event) => onSelect(Number(event.target.value))}
        className="rounded border border-slate-300 bg-white px-1 py-0.5 text-xs"
      >
        {parses.map((parse, i) => (
          <option key={parse.id} value={i}>
            {i + 1}
          </option>
        ))}
      </select>{" "}
      of {parses.length} in the c-/f-/a- views
    </label>
  );
}

export default App;
