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

// A feature is "valueless" when it carries nothing to show: an empty set, a
// null/blank scalar, or a ref to an f-node with no visible content (every feat
// of which is itself valueless — e.g. INTENS/DISTRIB pointing at an empty node).
// Valueless feats are hidden for now (a "Show Valueless Features" toggle may
// surface them later).
function isValueless(value: unknown, nodes: FStructureModel["nodes"], seen: Set<string>): boolean {
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

function sortedEntries(
  feats: Record<string, unknown>,
  nodes: FStructureModel["nodes"],
): [string, unknown][] {
  return Object.entries(feats)
    .filter(([, value]) => !isValueless(value, nodes, new Set()))
    .sort(([a], [b]) => attrRank(a) - attrRank(b) || a.localeCompare(b));
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
  nodes: FStructureModel["nodes"],
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

// A reentrancy tag: the f-node id, shown wherever a structure-shared node is
// referenced. All tags for one id share `data-fs-id`, so hovering any one
// highlights the whole structure-sharing set.
function Tag({
  fid,
  hovered,
  setHovered,
}: {
  fid: string;
  hovered: string | null;
  setHovered: (fid: string | null) => void;
}): ReactElement {
  const active = hovered === fid;
  return (
    <span
      data-fs-id={fid}
      onMouseOver={(event) => {
        event.stopPropagation();
        setHovered(fid);
      }}
      className={`cursor-default rounded px-1 text-[10px] ${
        active ? "bg-amber-200 text-amber-900" : "bg-slate-100 text-slate-500"
      }`}
    >
      {fid}
    </span>
  );
}

function ValueCell({
  value,
  hovered,
  setHovered,
}: {
  value: RowValue;
  hovered: string | null;
  setHovered: (fid: string | null) => void;
}): ReactElement | null {
  if (value.kind === "scalar") {
    return <span className="text-violet-700">{value.text}</span>;
  }
  if (value.kind === "ref") {
    return <Tag fid={value.fid} hovered={hovered} setHovered={setHovered} />;
  }
  if (value.kind === "set") {
    return (
      <span className="text-slate-400">
        {"{ "}
        {value.members.map((member, i) => (
          <Fragment key={i}>
            {i > 0 && <span className="text-slate-300">, </span>}
            {isFRef(member) ? (
              <Tag fid={member.$ref} hovered={hovered} setHovered={setHovered} />
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

// The F-structure tab body: the f-graph as an indented AVM. Attributes order
// canonically (PRED → predicate feats → GFs → adjuncts → nominal feats → LEMMA),
// nested nodes indent under their attribute (no boxes), and every value aligns
// in one shared column. Reentrant nodes carry a hoverable id tag; hovering any
// node (a row or a tag) cross-highlights it everywhere — controlled by the
// combined C/F view via `activeFid` + `onHoverNode`, otherwise internal.
export function FStructureView({
  result,
  selected,
  activeFid,
  onHoverNode,
}: {
  result: ParseResponse | undefined;
  selected: number;
  activeFid?: string | null;
  onHoverNode?: (id: string | null) => void;
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
  const refCounts = countRefs(fstruct.nodes);
  const rows: Row[] = [];
  flatten(fstruct.root, 0, new Set(), new Set(), refCounts, fstruct.nodes, rows);

  // One shared value column: wide enough for the deepest-indented longest
  // attribute, so every value lines up regardless of nesting (ch ~ one mono
  // char; +2 leaves a gap before the value).
  const valueCol = rows.reduce((m, r) => Math.max(m, r.depth * 2 + r.attr.length), 0) + 2;

  return (
    <div className="overflow-auto text-xs" onMouseLeave={() => setHovered(null)}>
      {rows.length === 0 ? (
        <span className="font-mono text-slate-400">[ ]</span>
      ) : (
        rows.map((row) => {
          const active = hovered === row.fid;
          return (
            <div
              key={row.key}
              data-fs-node={row.fid}
              onMouseOver={(event) => {
                event.stopPropagation();
                setHovered(row.fid);
              }}
              className={`flex rounded font-mono leading-6 ${active ? "bg-amber-50" : ""}`}
            >
              <span
                className={`shrink-0 ${active ? "text-amber-800" : "text-slate-500"}`}
                style={{ paddingLeft: `${row.depth * 2}ch`, width: `${valueCol}ch` }}
              >
                {row.attr}
              </span>
              <ValueCell value={row.value} hovered={hovered} setHovered={setHovered} />
            </div>
          );
        })
      )}
    </div>
  );
}
