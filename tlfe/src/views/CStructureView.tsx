// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { useMemo } from "react";

import type { CStructure, ParseResponse } from "../api/client";
import { type LaidOutNode, layoutCStructure } from "./cstructureLayout";

const EQ_DY_START = 14;
const EQ_LINE = 12;
const LABEL_ASCENT = 13;
const EQ_MAX_CHARS = 18;

// The C-structure tab: an empty/no-parse state, a parse selector when the
// response carries more than one complete parse (controlled from App so the
// other projection tabs will share the selection), and the SVG tree.
export function CStructureView({
  result,
  selected,
  onSelect,
}: {
  result: ParseResponse | undefined;
  selected: number;
  onSelect: (index: number) => void;
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
    <div className="flex flex-col gap-3">
      {parses.length > 1 && (
        <label className="text-xs text-slate-500">
          Parse{" "}
          <select
            value={index}
            onChange={(event) => onSelect(Number(event.target.value))}
            className="rounded border border-slate-300 bg-white px-1 py-0.5 text-xs"
          >
            {parses.map((parse, i) => (
              <option key={parse.id} value={i}>
                {i + 1}
              </option>
            ))}
          </select>{" "}
          of {parses.length}
        </label>
      )}
      <CStructureTree cstruct={parses[index].c_structure} />
    </div>
  );
}

function CStructureTree({ cstruct }: { cstruct: CStructure }) {
  const layout = useMemo(() => layoutCStructure(cstruct), [cstruct]);
  const byId = useMemo(() => {
    const map = new Map<string, LaidOutNode>();
    for (const node of layout.nodes) map.set(node.id, node);
    return map;
  }, [layout]);

  if (layout.nodes.length === 0) {
    return <p className="text-slate-400">Empty c-structure.</p>;
  }

  return (
    <div className="overflow-auto">
      <svg width={layout.width} height={layout.height} role="img" aria-label="c-structure tree">
        {layout.edges.map((edge) => {
          const from = byId.get(edge.from);
          const to = byId.get(edge.to);
          if (!from || !to) return null;
          const fromBottom =
            from.y +
            (from.equations.length > 0 ? EQ_DY_START + from.equations.length * EQ_LINE - 4 : 6);
          return (
            <line
              key={`${edge.from}-${edge.to}`}
              x1={from.x}
              y1={fromBottom}
              x2={to.x}
              y2={to.y - LABEL_ASCENT}
              stroke="currentColor"
              className="text-slate-300"
            />
          );
        })}
        {layout.nodes.map((node) => (
          <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
            {node.equations.length > 0 && <title>{node.equations.join("\n")}</title>}
            <text textAnchor="middle" className="fill-violet-700 text-[13px] font-medium">
              {node.label}
            </text>
            {node.equations.map((equation, i) => (
              <text
                key={i}
                textAnchor="middle"
                y={EQ_DY_START + i * EQ_LINE}
                className="fill-slate-400 text-[10px]"
              >
                {equation.length > EQ_MAX_CHARS
                  ? `${equation.slice(0, EQ_MAX_CHARS - 1)}…`
                  : equation}
              </text>
            ))}
          </g>
        ))}
      </svg>
    </div>
  );
}
