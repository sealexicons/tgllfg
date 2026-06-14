// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { Fragment, type ReactElement, useMemo, useState } from "react";
import { Popover } from "radix-ui";

import type { FStructureModel, ParseResponse } from "../api/client";

type FNodes = FStructureModel["nodes"];

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

// A feature is "valueless" when it carries nothing to show: an empty set, a
// null/blank scalar, or a ref to an f-node with no visible content (every feat
// of which is itself valueless — e.g. INTENS/DISTRIB pointing at an empty node).
// Valueless feats are hidden for now (a "Show Valueless Features" toggle may
// surface them later).
function isValueless(value: unknown, nodes: FNodes, seen: Set<string>): boolean {
  if (value == null || value === "") return true;
  if (Array.isArray(value)) return value.length === 0;
  if (isFRef(value)) {
    const target = value.$ref;
    if (seen.has(target)) return false; // part of a cycle → structural, keep
    const next = new Set(seen).add(target);
    const feats = nodes[target]?.feats ?? {};
    return Object.values(feats).every((v) => isValueless(v, nodes, next));
  }
  return false; // a scalar (including boolean false / 0) has a value
}

// Canonical attribute order, applied at every node: PRED, then predicate
// features, governable grammatical functions, adjuncts, nominal features, and
// LEMMA last; anything unlisted sorts alphabetically just before LEMMA.
const ATTR_ORDER = [
  "PRED",
  "VOICE",
  "ASPECT",
  "ASPECT_TYPE",
  "MOOD",
  "TENSE",
  "POLARITY",
  "NEG",
  "NEG_SCOPE",
  "LEX-ASTRUCT",
  "SUBJ",
  "OBJ",
  "OBJ2",
  "OBJ_THETA",
  "OBL",
  "COMP",
  "XCOMP",
  "POSS",
  "ADJ",
  "ADJUNCT",
  "XADJ",
  "CASE",
  "MARKER",
  "DEM",
  "DEF",
  "SPEC",
  "NUM",
  "PERS",
  "GEND",
];
const ATTR_RANK = new Map(ATTR_ORDER.map((attr, i) => [attr, i]));

function attrRank(attr: string): number {
  if (attr === "LEMMA") return ATTR_ORDER.length + 1; // always last
  return ATTR_RANK.get(attr) ?? ATTR_ORDER.length; // unlisted: alpha, before LEMMA
}

function sortedEntries(feats: Record<string, unknown>, nodes: FNodes): [string, unknown][] {
  return Object.entries(feats)
    .filter(([, value]) => !isValueless(value, nodes, new Set()))
    .sort(([a], [b]) => attrRank(a) - attrRank(b) || a.localeCompare(b));
}

// Count how often each f-node is referenced ($ref) across the whole structure.
// A node referenced >= 2 times is reentrant (structure-shared) and gets a
// hoverable tag so every occurrence can cross-highlight.
function countRefs(nodes: FNodes): Map<string, number> {
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

type RowValue =
  | { kind: "scalar"; text: string }
  | { kind: "ref"; fid: string } // reentrancy tag: first reentrant occ, or a repeat/cyclic ref
  | { kind: "set"; members: unknown[] }
  | { kind: "none" }; // a header that only introduces the indented node below

interface Row {
  key: string;
  fid: string; // the f-node this attribute belongs to (drives cross-highlight)
  attr: string;
  depth: number;
  value: RowValue;
}

// Flatten the f-graph into ordered, depth-tagged rows. A node expands at its
// first occurrence; a later or cyclic reference becomes a tag (keeps the walk
// finite and structure-sharing visible). A nested node's rows simply follow the
// introducing attribute at depth+1 — indentation, not a box, shows nesting.
function flatten(
  fid: string,
  depth: number,
  path: Set<string>,
  expanded: Set<string>,
  refCounts: Map<string, number>,
  nodes: FNodes,
  out: Row[],
): void {
  expanded.add(fid);
  const nextPath = new Set(path).add(fid);
  for (const [attr, value] of sortedEntries(nodes[fid]?.feats ?? {}, nodes)) {
    const key = `${fid}.${attr}`;
    if (isFRef(value)) {
      const target = value.$ref;
      if (expanded.has(target) || path.has(target)) {
        out.push({ key, fid, attr, depth, value: { kind: "ref", fid: target } });
      } else {
        const reentrant = (refCounts.get(target) ?? 0) >= 2;
        out.push({
          key,
          fid,
          attr,
          depth,
          value: reentrant ? { kind: "ref", fid: target } : { kind: "none" },
        });
        flatten(target, depth + 1, nextPath, expanded, refCounts, nodes, out);
      }
    } else if (Array.isArray(value)) {
      out.push({ key, fid, attr, depth, value: { kind: "set", members: value } });
    } else {
      out.push({ key, fid, attr, depth, value: { kind: "scalar", text: String(value) } });
    }
  }
}

// The hover + select wiring shared down the AVM tree. `hovered` / `setHovered`
// drive cross-highlight; `onSelect` (a clicked f-node id) lets the parent scroll
// the c-structure to that node's φ-image.
interface AvmHandlers {
  hovered: string | null;
  setHovered: (id: string | null) => void;
  onSelect?: (id: string) => void;
}

// A reentrancy tag: the f-node id, shown wherever a structure-shared node is
// referenced. All tags for one id share `data-fs-id`, so hovering any one
// cross-highlights the whole structure-sharing set. Clicking opens a popover
// with that f-node's sub-structure (same AVM format) and reports the id so the
// c-structure can scroll to its φ-image.
function Tag({
  fid,
  nodes,
  handlers,
}: {
  fid: string;
  nodes: FNodes;
  handlers: AvmHandlers;
}): ReactElement {
  const active = handlers.hovered === fid;
  return (
    <Popover.Root>
      <Popover.Trigger asChild>
        <span
          data-fs-id={fid}
          onMouseOver={(event) => {
            event.stopPropagation();
            handlers.setHovered(fid);
          }}
          onClick={() => handlers.onSelect?.(fid)}
          className={`cursor-pointer rounded px-1 text-[10px] ${
            active ? "bg-amber-200 text-amber-900" : "bg-slate-100 text-slate-500"
          }`}
        >
          {fid}
        </span>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          side="bottom"
          sideOffset={6}
          className="z-50 max-h-80 max-w-sm overflow-auto rounded-md border border-slate-200 bg-white p-3 shadow-lg"
        >
          <p className="mb-1.5 font-mono text-[10px] font-semibold text-violet-700">{fid}</p>
          <Avm root={fid} nodes={nodes} handlers={handlers} />
          <Popover.Arrow className="fill-white" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}

function ValueCell({
  value,
  nodes,
  handlers,
}: {
  value: RowValue;
  nodes: FNodes;
  handlers: AvmHandlers;
}): ReactElement | null {
  if (value.kind === "scalar") {
    return <span className="text-violet-700">{value.text}</span>;
  }
  if (value.kind === "ref") {
    return <Tag fid={value.fid} nodes={nodes} handlers={handlers} />;
  }
  if (value.kind === "set") {
    return (
      <span className="text-slate-400">
        {"{ "}
        {value.members.map((member, i) => (
          <Fragment key={i}>
            {i > 0 && <span className="text-slate-300">, </span>}
            {isFRef(member) ? (
              <Tag fid={member.$ref} nodes={nodes} handlers={handlers} />
            ) : (
              <span className="text-violet-700">{String(member)}</span>
            )}
          </Fragment>
        ))}
        {" }"}
      </span>
    );
  }
  return null;
}

// An attribute-value matrix rooted at `root`: the f-graph flattened to indented,
// aligned rows. Reused for the whole f-structure and, inside a Tag popover, for
// a referenced sub-structure.
function Avm({
  root,
  nodes,
  handlers,
}: {
  root: string;
  nodes: FNodes;
  handlers: AvmHandlers;
}): ReactElement {
  const refCounts = useMemo(() => countRefs(nodes), [nodes]);
  const rows = useMemo(() => {
    const out: Row[] = [];
    flatten(root, 0, new Set(), new Set(), refCounts, nodes, out);
    return out;
  }, [root, nodes, refCounts]);

  if (rows.length === 0) {
    return <span className="font-mono text-slate-400">[ ]</span>;
  }

  // One shared value column: wide enough for the deepest-indented longest
  // attribute, so every value lines up regardless of nesting (ch ~ one mono
  // char; +2 leaves a gap before the value).
  const valueCol = rows.reduce((m, r) => Math.max(m, r.depth * 2 + r.attr.length), 0) + 2;

  return (
    <>
      {rows.map((row) => {
        const active = handlers.hovered === row.fid;
        return (
          <div
            key={row.key}
            data-fs-node={row.fid}
            onMouseOver={(event) => {
              event.stopPropagation();
              handlers.setHovered(row.fid);
            }}
            className={`flex rounded font-mono leading-6 ${active ? "bg-amber-50" : ""}`}
          >
            <span
              className={`shrink-0 ${active ? "text-amber-800" : "text-slate-500"}`}
              style={{ paddingLeft: `${row.depth * 2}ch`, width: `${valueCol}ch` }}
            >
              {row.attr}
            </span>
            <ValueCell value={row.value} nodes={nodes} handlers={handlers} />
          </div>
        );
      })}
    </>
  );
}

// The F-structure tab body: the f-graph as an indented AVM. Attributes order
// canonically (PRED → predicate feats → GFs → adjuncts → nominal feats → LEMMA),
// nested nodes indent under their attribute (no boxes), and every value aligns
// in one shared column. Reentrant nodes carry a hoverable id tag; hovering any
// node cross-highlights it everywhere and clicking it opens a sub-structure
// popover + reports the id (via `onSelectNode`) so the c-structure can scroll to
// its φ-image. Hover is controlled by the combined C/F view via `activeFid` +
// `onHoverNode`, otherwise internal.
export function FStructureView({
  result,
  selected,
  activeFid,
  onHoverNode,
  onSelectNode,
}: {
  result: ParseResponse | undefined;
  selected: number;
  activeFid?: string | null;
  onHoverNode?: (id: string | null) => void;
  onSelectNode?: (id: string) => void;
}) {
  const [internalHover, setInternalHover] = useState<string | null>(null);
  const controlled = onHoverNode !== undefined;
  const hovered = controlled ? (activeFid ?? null) : internalHover;
  const setHovered = controlled ? onHoverNode : setInternalHover;

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
  const handlers: AvmHandlers = { hovered, setHovered, onSelect: onSelectNode };

  return (
    <div className="overflow-auto text-xs" onMouseLeave={() => setHovered(null)}>
      <Avm root={fstruct.root} nodes={fstruct.nodes} handlers={handlers} />
    </div>
  );
}
