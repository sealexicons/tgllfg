// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { Fragment, type ReactElement, useState } from "react";

import type { FStructureModel, ParseResponse } from "../api/client";

interface FRef {
  $ref: string;
}

function isFRef(value: unknown): value is FRef {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value) &&
    typeof (value as { $ref?: unknown }).$ref === "string"
  );
}

// Count how often each f-node is referenced ($ref) across the whole structure.
// A node referenced >= 2 times is reentrant (structure-shared) and gets a
// hoverable tag so every occurrence can cross-highlight.
function countRefs(nodes: FStructureModel["nodes"]): Map<string, number> {
  const counts = new Map<string, number>();
  const tally = (value: unknown): void => {
    if (isFRef(value)) {
      counts.set(value.$ref, (counts.get(value.$ref) ?? 0) + 1);
    } else if (Array.isArray(value)) {
      value.forEach(tally);
    }
  };
  for (const node of Object.values(nodes)) {
    for (const value of Object.values(node.feats ?? {})) tally(value);
  }
  return counts;
}

interface RenderCtx {
  nodes: FStructureModel["nodes"];
  refCounts: Map<string, number>;
  expanded: Set<string>;
  hovered: string | null;
  setHovered: (fid: string | null) => void;
}

// A reentrancy tag: the f-node id, shown at the node's expansion and at every
// later $ref to it. All tags for one id share `data-fs-id`, so hovering any
// one highlights the whole structure-sharing set.
function Tag({ fid, ctx }: { fid: string; ctx: RenderCtx }): ReactElement {
  const active = ctx.hovered === fid;
  return (
    <span
      data-fs-id={fid}
      onMouseEnter={() => ctx.setHovered(fid)}
      onMouseLeave={() => ctx.setHovered(null)}
      className={`cursor-default rounded px-1 font-mono text-[10px] ${
        active ? "bg-amber-200 text-amber-900" : "bg-slate-100 text-slate-500"
      }`}
    >
      {fid}
    </span>
  );
}

function renderValue(value: unknown, path: Set<string>, ctx: RenderCtx): ReactElement {
  if (isFRef(value)) {
    const target = value.$ref;
    // Expand a node at its first occurrence; a later or cyclic reference shows
    // just the tag (keeps the render finite and structure-sharing visible).
    if (ctx.expanded.has(target) || path.has(target)) {
      return <Tag fid={target} ctx={ctx} />;
    }
    return renderNode(target, path, ctx);
  }
  if (Array.isArray(value)) {
    return (
      <span className="text-slate-400">
        {"{ "}
        {value.map((member, i) => (
          <Fragment key={i}>
            {i > 0 && <span className="text-slate-300">, </span>}
            {renderValue(member, path, ctx)}
          </Fragment>
        ))}
        {" }"}
      </span>
    );
  }
  return <span className="font-mono text-xs text-violet-700">{String(value)}</span>;
}

function renderNode(fid: string, path: Set<string>, ctx: RenderCtx): ReactElement {
  ctx.expanded.add(fid);
  const node = ctx.nodes[fid];
  const entries = Object.entries(node?.feats ?? {});
  const reentrant = (ctx.refCounts.get(fid) ?? 0) >= 2;
  const nextPath = new Set(path).add(fid);

  return (
    <span className="inline-flex items-start gap-1 align-top">
      {reentrant && <Tag fid={fid} ctx={ctx} />}
      <span className="inline-block rounded border border-slate-300 bg-white px-2 py-1">
        {entries.length === 0 ? (
          <span className="font-mono text-xs text-slate-400">[ ]</span>
        ) : (
          <span className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
            {entries.map(([attr, value]) => (
              <Fragment key={attr}>
                <span className="font-mono text-xs font-medium text-slate-500">{attr}</span>
                <span>{renderValue(value, nextPath, ctx)}</span>
              </Fragment>
            ))}
          </span>
        )}
      </span>
    </span>
  );
}

// The F-structure tab: the f-graph as a nested AVM. Reentrant (structure-
// shared) nodes carry a hoverable id tag at each occurrence so hovering one
// cross-highlights all of them. Selection is controlled from App.
export function FStructureView({
  result,
  selected,
}: {
  result: ParseResponse | undefined;
  selected: number;
}) {
  const [hovered, setHovered] = useState<string | null>(null);

  if (!result) {
    return <p className="text-slate-400">Parse a sentence to see its f-structure.</p>;
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
  const fstruct = parses[index].f_structure;
  const ctx: RenderCtx = {
    nodes: fstruct.nodes,
    refCounts: countRefs(fstruct.nodes),
    expanded: new Set(),
    hovered,
    setHovered,
  };

  return <div className="overflow-auto">{renderNode(fstruct.root, new Set(), ctx)}</div>;
}
