// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import type { DiagnosticModel, ParseResponse } from "../api/client";

function DiagnosticRow({ d }: { d: DiagnosticModel }) {
  const hasMeta = Boolean(d.cnode_label) || Boolean(d.equation) || (d.path?.length ?? 0) > 0;
  return (
    <li className="rounded border border-slate-200 px-3 py-2">
      <div className="flex items-center gap-2">
        <span
          className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
            d.blocking ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
          }`}
        >
          {d.blocking ? "blocking" : "note"}
        </span>
        <span className="font-mono text-xs text-slate-500">{d.kind}</span>
      </div>
      <p className="mt-1 text-sm text-slate-700">{d.message}</p>
      {hasMeta && (
        <dl className="mt-1 grid grid-cols-[auto_1fr] gap-x-2 gap-y-0.5 text-xs text-slate-500">
          {d.cnode_label && (
            <>
              <dt className="font-medium">c-node</dt>
              <dd className="font-mono">{d.cnode_label}</dd>
            </>
          )}
          {d.equation && (
            <>
              <dt className="font-medium">equation</dt>
              <dd className="font-mono">{d.equation}</dd>
            </>
          )}
          {d.path && d.path.length > 0 && (
            <>
              <dt className="font-medium">path</dt>
              <dd className="font-mono">{d.path.join(" ")}</dd>
            </>
          )}
        </dl>
      )}
    </li>
  );
}

// The Diagnostics tab: the selected parse's diagnostics, or — when there is no
// complete parse — the diagnostics from each fragment (labelled by span). Each
// row shows kind / message / blocking plus the c-node anchor, failing
// equation, and path when present.
export function DiagnosticsView({
  result,
  selected,
}: {
  result: ParseResponse | undefined;
  selected: number;
}) {
  if (!result) {
    return <p className="text-slate-400">Parse a sentence to see diagnostics.</p>;
  }

  const parses = result.parses ?? [];
  if (parses.length > 0) {
    const index = Math.min(Math.max(selected, 0), parses.length - 1);
    const diagnostics = parses[index].diagnostics ?? [];
    if (diagnostics.length === 0) {
      return <p className="text-slate-400">{`No diagnostics for parse ${index + 1}.`}</p>;
    }
    return (
      <ul className="flex flex-col gap-2">
        {diagnostics.map((d) => (
          <DiagnosticRow key={d.id} d={d} />
        ))}
      </ul>
    );
  }

  const fragments = result.fragments ?? [];
  const anyDiags = fragments.some((f) => (f.diagnostics?.length ?? 0) > 0);
  if (!anyDiags) {
    return <p className="text-slate-400">No diagnostics.</p>;
  }
  return (
    <div className="flex flex-col gap-3">
      {fragments.map((fragment, fi) =>
        (fragment.diagnostics?.length ?? 0) === 0 ? null : (
          <div key={fi}>
            <div className="mb-1 text-xs font-medium text-slate-500">
              {`Fragment [${fragment.span[0]}, ${fragment.span[1]}]`}
            </div>
            <ul className="flex flex-col gap-2">
              {(fragment.diagnostics ?? []).map((d) => (
                <DiagnosticRow key={`${fi}-${d.id}`} d={d} />
              ))}
            </ul>
          </div>
        ),
      )}
    </div>
  );
}
