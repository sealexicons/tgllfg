// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { Tabs, Tooltip } from "radix-ui";

// The three inspector views, rendered for real in Phase 14. Here they are
// placeholder panels that prove the Radix Tabs + Tailwind wiring.
const VIEWS = [
  {
    value: "cstructure",
    label: "C-structure",
    blurb: "Phrase-structure tree — rendered in Phase 14.",
  },
  {
    value: "fstructure",
    label: "F-structure",
    blurb: "Attribute-value matrix with reentrancies — rendered in Phase 14.",
  },
  {
    value: "json",
    label: "JSON",
    blurb: "Raw parse payload from the Phase 13 REST API.",
  },
] as const;

function App() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 px-6 py-10 text-slate-800">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">tgllfg inspector</h1>
        <p className="text-sm text-slate-500">
          Tagalog LFG parser — web inspector scaffold (Phase 12.D).
        </p>
      </header>

      <section className="flex items-center gap-2">
        <input
          type="text"
          disabled
          placeholder="Bumili ng aklat ang bata."
          aria-label="Tagalog sentence"
          className="flex-1 rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-400"
        />
        <Tooltip.Provider delayDuration={200}>
          <Tooltip.Root>
            <Tooltip.Trigger asChild>
              <button
                type="button"
                disabled
                className="rounded-md bg-violet-600 px-4 py-2 text-sm font-medium text-white opacity-60"
              >
                Parse
              </button>
            </Tooltip.Trigger>
            <Tooltip.Portal>
              <Tooltip.Content
                sideOffset={6}
                className="rounded bg-slate-900 px-2 py-1 text-xs text-white shadow"
              >
                Parsing is wired to the REST API in Phase 13/14.
                <Tooltip.Arrow className="fill-slate-900" />
              </Tooltip.Content>
            </Tooltip.Portal>
          </Tooltip.Root>
        </Tooltip.Provider>
      </section>

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
            className="rounded-md border border-dashed border-slate-300 p-6 text-sm text-slate-500"
          >
            {view.blurb}
          </Tabs.Content>
        ))}
      </Tabs.Root>
    </main>
  );
}

export default App;
