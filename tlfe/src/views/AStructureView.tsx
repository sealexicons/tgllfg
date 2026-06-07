// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { Fragment } from "react";

import type { ParseResponse } from "../api/client";

// The A-structure tab: the predicate's argument structure and its LMT mapping
// to grammatical functions (pred + ordered theta roles + role→GF). Selection
// is controlled from App.
export function AStructureView({
  result,
  selected,
}: {
  result: ParseResponse | undefined;
  selected: number;
}) {
  if (!result) {
    return <p className="text-slate-400">Parse a sentence to see its a-structure.</p>;
  }

  const parses = result.parses ?? [];
  if (parses.length === 0) {
    const frags = result.meta.fragment_count;
    return (
      <p className="text-slate-500">
        No complete parse
        {frags > 0 ? ` — ${frags} fragment${frags === 1 ? "" : "s"}` : ""}. See the JSON tab.
      </p>
    );
  }

  const index = Math.min(Math.max(selected, 0), parses.length - 1);
  const a = parses[index].a_structure;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-xs font-medium text-slate-500">PRED</span>
        <span className="font-mono text-sm text-violet-700">{a.pred}</span>
      </div>
      <div>
        <div className="mb-1 text-xs font-medium text-slate-500">Roles → grammatical functions</div>
        {a.roles.length === 0 ? (
          <p className="text-slate-400">No roles.</p>
        ) : (
          <div className="grid grid-cols-[auto_auto] gap-x-3 gap-y-1">
            {a.roles.map((role, i) => (
              <Fragment key={i}>
                <span className="font-mono text-xs text-slate-600">{role}</span>
                <span className="font-mono text-xs text-violet-700">
                  → {a.mapping[role] ?? "(unmapped)"}
                </span>
              </Fragment>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
