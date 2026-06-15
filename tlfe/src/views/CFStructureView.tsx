// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { useMemo, useState } from "react";

import type { ParseResponse } from "../api/client";
import { CStructureView } from "./CStructureView";
import { FStructureView } from "./FStructureView";

type NodeSel = { kind: "c" | "f"; id: string } | null;

// The combined C / F view: the c-structure tree and the f-structure AVM side by
// side, wired together by the φ correspondence (c-node id → f-node id) the
// parse endpoint returns. Hovering a c-node lights the f-node it projects to and
// every co-projecting c-node (the φ-sharing set); hovering an f-node lights
// every c-node that projects to it. Clicking pins the selection (so it survives
// the pointer moving away) and scrolls the *other* panel to its φ-image: an
// f-node click scrolls the c-tree, a c-node's "Show φ" scrolls the AVM
// (post-10). The two panels are otherwise the standalone views.
export function CFStructureView({
  result,
  selected,
}: {
  result: ParseResponse | undefined;
  selected: number;
}) {
  // `hover` follows the mouse (transient); `pinned` persists a click-selection
  // so a scrolled-to node stays highlighted after the pointer moves away. The
  // active highlight is hover ?? pinned.
  const [hover, setHover] = useState<NodeSel>(null);
  const [pinned, setPinned] = useState<NodeSel>(null);
  // Scroll targets, each with a bumped nonce so a repeat selection re-fires:
  // `cScroll` centres an f-node's φ-image in the c-tree (an f-node was clicked);
  // `fScroll` centres a c-node's φ-image in the AVM (a c-node's "Show φ").
  const [cScroll, setCScroll] = useState<{ cids: readonly string[]; nonce: number }>({
    cids: [],
    nonce: 0,
  });
  const [fScroll, setFScroll] = useState<{ fid: string; nonce: number }>({
    fid: "",
    nonce: 0,
  });

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

  // Clicking an f-node pins it + scrolls the c-structure to the c-node(s) it
  // projects from (its φ-image); a φ-orphaned f-node yields an empty target.
  function selectFNode(fid: string) {
    setPinned({ kind: "f", id: fid });
    setCScroll((prev) => ({ cids: cIdsByF.get(fid) ?? [], nonce: prev.nonce + 1 }));
  }

  // A c-node's "Show φ" / φ-link pins its φ-image f-node + scrolls the AVM to it.
  function selectFNodeFromC(fid: string) {
    setPinned({ kind: "f", id: fid });
    setFScroll((prev) => ({ fid, nonce: prev.nonce + 1 }));
  }

  // Hover wins while the pointer is over a node; otherwise the pinned click.
  const active = hover ?? pinned;
  let activeF: string | null = null;
  let activeCs = new Set<string>();
  if (active?.kind === "c") {
    activeF = correspondence[active.id] ?? null;
    activeCs = new Set(activeF ? (cIdsByF.get(activeF) ?? [active.id]) : [active.id]);
  } else if (active?.kind === "f") {
    activeF = active.id;
    activeCs = new Set(cIdsByF.get(active.id) ?? []);
  }

  return (
    <div className="flex flex-col gap-6 lg:flex-row lg:items-stretch lg:gap-0">
      <section className="flex flex-col gap-2 lg:min-w-0 lg:flex-1">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          C-structure
        </h3>
        <CStructureView
          result={result}
          selected={selected}
          highlight={activeCs}
          scrollTo={cScroll}
          correspondence={correspondence}
          onHoverNode={(id) => setHover(id ? { kind: "c", id } : null)}
          onSelectFNode={selectFNodeFromC}
        />
      </section>
      <div
        aria-hidden="true"
        className="hidden lg:mx-6 lg:my-2 lg:block lg:w-0.5 lg:self-stretch lg:bg-slate-300"
      />
      <section className="flex flex-col gap-2 lg:max-w-md lg:flex-none">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          F-structure
        </h3>
        <FStructureView
          result={result}
          selected={selected}
          activeFid={activeF}
          scrollTo={fScroll}
          onHoverNode={(id) => setHover(id ? { kind: "f", id } : null)}
          onSelectNode={selectFNode}
        />
      </section>
    </div>
  );
}
