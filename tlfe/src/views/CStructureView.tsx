// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { useMemo } from "react";
import { Popover } from "radix-ui";

import type { CStructure, ParseResponse } from "../api/client";
import { type LaidOutNode, layoutCStructure } from "./cstructureLayout";

const LABEL_ASCENT = 13;
const HALO_H = 20;
// Edges leave a node from the bottom of its label halo (HALO_H - LABEL_ASCENT).
const EDGE_DROP = HALO_H - LABEL_ASCENT;
const ARC_RISE = 24;

// The C-structure tab body: empty/no-parse and fragment-only states plus the
// SVG tree for the selected parse (selection is controlled from App). Each node
// shows only its category label; its functional equations open in a click
// popover (Phase 14.final.post-1) so dense trees stay legible. When the optional
// `highlight` set / `onHoverNode` callback are supplied (by the combined C/F
// view) the tree highlights those nodes, draws φ-sharing arcs between them, and
// reports hover so the f-structure can cross-highlight.
export function CStructureView({
  result,
  selected,
  highlight,
  onHoverNode,
}: {
  result: ParseResponse | undefined;
  selected: number;
  highlight?: ReadonlySet<string>;
  onHoverNode?: (id: string | null) => void;
}) {
  if (!result) {
    return <p className="text-slate-400">Parse a sentence to see its c-structure.</p>;
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
  return (
    <CStructureTree
      cstruct={parses[index].c_structure}
      highlight={highlight}
      onHoverNode={onHoverNode}
    />
  );
}

function CStructureTree({
  cstruct,
  highlight,
  onHoverNode,
}: {
  cstruct: CStructure;
  highlight?: ReadonlySet<string>;
  onHoverNode?: (id: string | null) => void;
}) {
  const layout = useMemo(() => layoutCStructure(cstruct), [cstruct]);
  const byId = useMemo(() => {
    const map = new Map<string, LaidOutNode>();
    for (const node of layout.nodes) map.set(node.id, node);
    return map;
  }, [layout]);

  if (layout.nodes.length === 0) {
    return <p className="text-slate-400">Empty c-structure.</p>;
  }

  // φ-sharing arcs: connect the highlighted (co-projecting) nodes left to right
  // with shallow upward Béziers — the c-structure echo of f-structure
  // reentrancy (several c-nodes projecting one f-node).
  const lit = highlight
    ? layout.nodes.filter((n) => highlight.has(n.id)).sort((a, b) => a.x - b.x || a.y - b.y)
    : [];
  const arcs =
    lit.length >= 2
      ? lit.slice(1).map((to, i) => {
          const from = lit[i];
          const ay = from.y - LABEL_ASCENT;
          const by = to.y - LABEL_ASCENT;
          const cy = Math.min(ay, by) - ARC_RISE;
          return {
            key: `${from.id}-${to.id}`,
            d: `M ${from.x} ${ay} Q ${(from.x + to.x) / 2} ${cy} ${to.x} ${by}`,
          };
        })
      : [];

  return (
    <div className="overflow-auto">
      <svg
        width={layout.width}
        height={layout.height}
        role="img"
        aria-label="c-structure tree"
        onMouseLeave={() => onHoverNode?.(null)}
      >
        {layout.edges.map((edge) => {
          const from = byId.get(edge.from);
          const to = byId.get(edge.to);
          if (!from || !to) return null;
          return (
            <line
              key={`${edge.from}-${edge.to}`}
              x1={from.x}
              y1={from.y + EDGE_DROP}
              x2={to.x}
              y2={to.y - LABEL_ASCENT}
              stroke="currentColor"
              className="text-slate-300"
            />
          );
        })}
        {arcs.map((arc) => (
          <path
            key={arc.key}
            d={arc.d}
            fill="none"
            stroke="currentColor"
            strokeWidth={1.5}
            className="text-amber-400"
          />
        ))}
        {layout.nodes.map((node) => (
          <CStructureNode
            key={node.id}
            node={node}
            active={highlight?.has(node.id) ?? false}
            onHoverNode={onHoverNode}
          />
        ))}
      </svg>
    </div>
  );
}

// A single tree node: a category label inside a (transparent until lit) halo
// that opens a popover of the node's functional equations on click. The label
// alone keeps the tree readable; the equation stack was what overlapped when it
// was drawn inline under every node (Phase 14.final.post-1).
function CStructureNode({
  node,
  active,
  onHoverNode,
}: {
  node: LaidOutNode;
  active: boolean;
  onHoverNode?: (id: string | null) => void;
}) {
  const haloW = node.label.length * 7 + 10;
  return (
    <Popover.Root>
      <Popover.Trigger asChild>
        <g
          transform={`translate(${node.x}, ${node.y})`}
          tabIndex={0}
          aria-label={node.label}
          style={{ cursor: "pointer" }}
          onMouseOver={(event) => {
            event.stopPropagation();
            onHoverNode?.(node.id);
          }}
        >
          <rect
            x={-haloW / 2}
            y={-LABEL_ASCENT}
            width={haloW}
            height={HALO_H}
            rx={4}
            className={active ? "fill-amber-100" : "fill-transparent"}
            style={{ pointerEvents: "all" }}
          />
          <text
            textAnchor="middle"
            className={
              active
                ? "fill-amber-800 text-[13px] font-semibold"
                : "fill-violet-700 text-[13px] font-medium"
            }
          >
            {node.label}
          </text>
        </g>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          side="bottom"
          sideOffset={6}
          className="z-50 max-w-sm rounded-md border border-slate-200 bg-white p-3 text-xs shadow-lg"
        >
          <p className="mb-1.5 font-semibold text-violet-700">{node.label}</p>
          {node.equations.length > 0 ? (
            <ul className="space-y-0.5 font-mono leading-relaxed text-slate-600">
              {node.equations.map((equation, i) => (
                <li key={i}>{equation}</li>
              ))}
            </ul>
          ) : (
            <p className="text-slate-400">No functional equations.</p>
          )}
          <Popover.Arrow className="fill-white" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}
