// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { useMemo, useState } from "react";

import type { ParseResponse } from "../api/client";
import { CStructureView } from "./CStructureView";
import { FStructureView } from "./FStructureView";

type Hover = { kind: "c" | "f"; id: string } | null;

// The combined C / F view: the c-structure tree and the f-structure AVM side by
// side, wired together by the φ correspondence (c-node id → f-node id) the
// parse endpoint now returns. Hovering a c-node lights the f-node it projects
// to and every co-projecting c-node (the φ-sharing set); hovering an f-node
// lights every c-node that projects to it. The two panels are otherwise the
// standalone views, driven here by one shared hover state.
export function CFStructureView({
  result,
  selected,
}: {
  result: ParseResponse | undefined;
  selected: number;
}) {
  const [hover, setHover] = useState<Hover>(null);

  const parses = result?.parses ?? [];
  const index = Math.min(Math.max(selected, 0), Math.max(parses.length - 1, 0));
  const parse = parses[index];

  // φ as given (c → f) plus its inverse (f → [c]); recomputed per parse.
  const { correspondence, cIdsByF } = useMemo(() => {
    const corr: Record<string, string> = parse?.correspondence ?? {};
    const inv = new Map<string, string[]>();
    for (const [cId, fId] of Object.entries(corr)) {
      const list = inv.get(fId);
      if (list) list.push(cId);
      else inv.set(fId, [cId]);
    }
    return { correspondence: corr, cIdsByF: inv };
  }, [parse]);

  let activeF: string | null = null;
  let activeCs = new Set<string>();
  if (hover?.kind === "c") {
    activeF = correspondence[hover.id] ?? null;
    activeCs = new Set(activeF ? (cIdsByF.get(activeF) ?? [hover.id]) : [hover.id]);
  } else if (hover?.kind === "f") {
    activeF = hover.id;
    activeCs = new Set(cIdsByF.get(hover.id) ?? []);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <section className="flex flex-col gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          C-structure
        </h3>
        <CStructureView
          result={result}
          selected={selected}
          highlight={activeCs}
          onHoverNode={(id) => setHover(id ? { kind: "c", id } : null)}
        />
      </section>
      <section className="flex flex-col gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          F-structure
        </h3>
        <FStructureView
          result={result}
          selected={selected}
          activeFid={activeF}
          onHoverNode={(id) => setHover(id ? { kind: "f", id } : null)}
        />
      </section>
    </div>
  );
}
