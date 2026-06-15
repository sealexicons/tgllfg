// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { type ReactNode, useEffect, useMemo, useRef } from "react";
import { ContextMenu, Popover } from "radix-ui";

import type { CStructure, ParseResponse } from "../api/client";
import { useLexSearch } from "../api/hooks";
import { displayLabel, labelWidth, type LaidOutNode, layoutCStructure } from "./cstructureLayout";

const LABEL_ASCENT = 13;
const HALO_H = 20;
// Edges leave a node from the bottom of its label halo (HALO_H - LABEL_ASCENT).
const EDGE_DROP = HALO_H - LABEL_ASCENT;
const ARC_RISE = 24;
// Equal left/right breathing room inside the SVG around the tree's true extent.
const VIEW_PAD = 16;

// A request to scroll the tree so the given c-nodes are visible; the nonce makes
// a repeated request for the same nodes still fire.
interface ScrollTarget {
  cids: readonly string[];
  nonce: number;
}

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
  scrollTo,
  correspondence,
  onHoverNode,
  onSelectFNode,
}: {
  result: ParseResponse | undefined;
  selected: number;
  highlight?: ReadonlySet<string>;
  scrollTo?: ScrollTarget;
  // φ as given (c-node id → f-node id) so a node can offer "Show φ" (post-10).
  correspondence?: Record<string, string>;
  onHoverNode?: (id: string | null) => void;
  onSelectFNode?: (fid: string) => void;
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
      scrollTo={scrollTo}
      correspondence={correspondence}
      onHoverNode={onHoverNode}
      onSelectFNode={onSelectFNode}
    />
  );
}

function CStructureTree({
  cstruct,
  highlight,
  scrollTo,
  correspondence,
  onHoverNode,
  onSelectFNode,
}: {
  cstruct: CStructure;
  highlight?: ReadonlySet<string>;
  scrollTo?: ScrollTarget;
  correspondence?: Record<string, string>;
  onHoverNode?: (id: string | null) => void;
  onSelectFNode?: (fid: string) => void;
}) {
  const layout = useMemo(() => layoutCStructure(cstruct), [cstruct]);
  const byId = useMemo(() => {
    const map = new Map<string, LaidOutNode>();
    for (const node of layout.nodes) map.set(node.id, node);
    return map;
  }, [layout]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // The tidy-tree pads the right edge by an extra column and ignores label
  // width, so layout.width is lopsided. Re-derive the real horizontal extent
  // (label halos included) and pad both sides equally so the mx-auto-centred SVG
  // actually looks centred. Computed before any early return so the scroll
  // effect (a hook) can sit above it.
  let minX = Infinity;
  let maxX = -Infinity;
  for (const node of layout.nodes) {
    const half = labelWidth(displayLabel(node.label)) / 2;
    minX = Math.min(minX, node.x - half);
    maxX = Math.max(maxX, node.x + half);
  }
  const dx = VIEW_PAD - minX;
  const width = VIEW_PAD * 2 + maxX - minX;

  // Centre a clicked f-node's φ-image c-nodes in view (smooth scroll). A
  // φ-orphaned f-node yields no targets, so nothing moves.
  useEffect(() => {
    const el = scrollRef.current;
    if (!el || !scrollTo || scrollTo.cids.length === 0) return;
    const targets = scrollTo.cids
      .map((id) => byId.get(id))
      .filter((n): n is LaidOutNode => n !== undefined);
    if (targets.length === 0) return;
    const xs = targets.map((n) => n.x + dx);
    const ys = targets.map((n) => n.y);
    el.scrollTo({
      left: (Math.min(...xs) + Math.max(...xs)) / 2 - el.clientWidth / 2,
      top: (Math.min(...ys) + Math.max(...ys)) / 2 - el.clientHeight / 2,
      behavior: "smooth",
    });
  }, [scrollTo, byId, dx]);

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
          // Vertically-stacked co-projecting nodes (a head and its phrase): trace
          // the plain tree edge (upper halo-bottom → lower halo-top) so the
          // highlight matches the grey connector instead of bulging above the top
          // node. Horizontally-separated nodes keep the shallow upward arc.
          if (from.x === to.x) {
            const upper = from.y <= to.y ? from : to;
            const lower = from.y <= to.y ? to : from;
            return {
              key: `${from.id}-${to.id}`,
              d: `M ${upper.x} ${upper.y + EDGE_DROP} L ${lower.x} ${lower.y - LABEL_ASCENT}`,
            };
          }
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
    <div ref={scrollRef} className="overflow-auto lg:min-h-0 lg:flex-1">
      <svg
        width={width}
        height={layout.height}
        role="img"
        aria-label="c-structure tree"
        onMouseLeave={() => onHoverNode?.(null)}
        // The SVG is sized to the tree's true extent with equal side padding,
        // then mx-auto centres it (margins collapse to 0 when it overflows, so
        // wide trees still left-align and scroll).
        className="mx-auto block"
      >
        <g transform={`translate(${dx}, 0)`}>
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
              phiFid={correspondence?.[node.id]}
              onHoverNode={onHoverNode}
              onSelectFNode={onSelectFNode}
            />
          ))}
        </g>
      </svg>
    </div>
  );
}

// The citation lemma a terminal node carries, pulled from its `(↑ LEMMA) = '…'`
// equation (nouns / preps / particles / adjectives have one; verbs are
// PRED-only, so they get no gloss lookup). Drives the context-menu gloss.
function lemmaOf(node: LaidOutNode): string | null {
  for (const equation of node.equations ?? []) {
    const match = /\(↑ LEMMA\)\s*=\s*'([^']*)'/.exec(equation);
    if (match) return match[1];
  }
  return null;
}

// Glosses for a terminal's lemma, fetched lazily (only while the context menu
// is open) from the existing /lex/search endpoint and filtered to exact
// citation-form matches — informational labels, not actions. Postgres-backed,
// so it degrades to "unavailable" when the DB isn't wired.
function GlossItems({ lemma }: { lemma: string }): ReactNode {
  const { data, isLoading, isError } = useLexSearch({ q: lemma, limit: 10 });
  const rowCls = "px-2 py-0.5 text-xs";
  if (isLoading) return <div className={`${rowCls} text-slate-400`}>loading…</div>;
  if (isError) return <div className={`${rowCls} text-slate-400`}>gloss unavailable</div>;
  const exact = (data?.matches ?? []).filter((m) => m.citation_form === lemma && m.gloss);
  if (exact.length === 0) {
    return <div className={`${rowCls} text-slate-400`}>no gloss</div>;
  }
  return (
    <>
      {exact.map((m) => (
        <div key={m.id} className={`${rowCls} text-slate-700`}>
          <span className="text-slate-400">{m.pos}</span> {m.gloss}
        </div>
      ))}
    </>
  );
}

// A single tree node: a category label inside a (transparent until lit) halo.
// Left-click opens a Radix Popover of the node's functional equations (Phase
// 14.final.post-1); right-click opens a context menu (post-10) with "Show φ"
// (scroll the f-structure to this node's φ-image) and, for a terminal, its
// gloss. The φ-image is also a link in the equation popover header. The label
// alone keeps the tree readable; the equation stack overlapped when drawn inline.
function CStructureNode({
  node,
  active,
  phiFid,
  onHoverNode,
  onSelectFNode,
}: {
  node: LaidOutNode;
  active: boolean;
  phiFid?: string;
  onHoverNode?: (id: string | null) => void;
  onSelectFNode?: (fid: string) => void;
}) {
  const label = displayLabel(node.label);
  const haloW = labelWidth(label);
  const lemma = lemmaOf(node);
  const itemCls =
    "cursor-pointer rounded px-2 py-1 text-xs outline-none data-[highlighted]:bg-violet-50";
  return (
    <Popover.Root>
      <ContextMenu.Root>
        <ContextMenu.Trigger asChild>
          <Popover.Trigger asChild>
            <g
              transform={`translate(${node.x}, ${node.y})`}
              tabIndex={0}
              aria-label={label}
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
                {label}
              </text>
            </g>
          </Popover.Trigger>
        </ContextMenu.Trigger>
        <ContextMenu.Portal>
          <ContextMenu.Content className="z-50 min-w-44 rounded-md border border-slate-200 bg-white p-1 text-xs shadow-lg">
            {phiFid ? (
              <ContextMenu.Item className={itemCls} onSelect={() => onSelectFNode?.(phiFid)}>
                Show φ → <span className="font-mono text-violet-700">{phiFid}</span>
              </ContextMenu.Item>
            ) : (
              <div className="px-2 py-1 text-xs text-slate-400">no φ-image</div>
            )}
            {lemma !== null && (
              <>
                <ContextMenu.Separator className="my-1 h-px bg-slate-200" />
                <div className="px-2 pb-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                  gloss · {lemma}
                </div>
                <GlossItems lemma={lemma} />
              </>
            )}
          </ContextMenu.Content>
        </ContextMenu.Portal>
      </ContextMenu.Root>
      <Popover.Portal>
        <Popover.Content
          side="bottom"
          sideOffset={6}
          className="z-50 max-w-sm rounded-md border border-slate-200 bg-white p-3 text-xs shadow-lg"
        >
          <div className="mb-1.5 flex items-baseline justify-between gap-3">
            <p className="font-semibold text-violet-700">{label}</p>
            {phiFid && (
              <Popover.Close asChild>
                <button
                  type="button"
                  onClick={() => onSelectFNode?.(phiFid)}
                  className="shrink-0 rounded px-1 font-mono text-[10px] text-violet-600 hover:bg-violet-50"
                >
                  φ → {phiFid}
                </button>
              </Popover.Close>
            )}
          </div>
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
