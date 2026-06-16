// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import type { CStructure } from "../api/client";

export interface LaidOutNode {
  id: string;
  label: string;
  equations: string[];
  // The terminal's licensing lexical gloss (POS-correct, from the entry that
  // actually projected this node); null on non-terminals and glossless word
  // classes. Drives the context-menu gloss (Phase 14.final.post-11).
  gloss: string | null;
  x: number;
  y: number;
}

export interface LaidOutEdge {
  from: string;
  to: string;
}

export interface TreeLayout {
  nodes: LaidOutNode[];
  edges: LaidOutEdge[];
  width: number;
  height: number;
}

// Display form of a category label: a binary feature that is simply true shows
// as just its name (N[N_CORE] not N[N_CORE=True]); enum/other values (CASE=NOM)
// are kept. Display-only; the raw label stays in the JSON payload.
export const displayLabel = (label: string) => label.replace(/=True\b/g, "");

// Rough on-screen width of a node label's halo. Sized a little generously so the
// active (bold) label stays inside its highlight — and it drives the layout, so
// wide labels reserve real horizontal room rather than overrunning neighbours.
export const labelWidth = (label: string) => label.length * 8 + 14;

// Vertical row pitch + outer padding + the minimum gap between sibling blocks
// (px). The horizontal layout is width-aware: each subtree occupies a block as
// wide as the larger of its own label and its children's span, so a wide label
// like PUNCT[PUNCT_CLASS=COMMA] no longer overlaps its neighbour.
export const NODE_Y_GAP = 56;
export const TREE_PAD = 36;
export const SIBLING_GAP = 24;

/**
 * Lay out a c-structure node table as a width-aware "block" tree: each subtree
 * is allocated a block whose width is the larger of its own label width and its
 * children's combined block widths (plus gaps). Children are centred as a group
 * beneath their parent, and each parent sits over the midpoint of its first and
 * last child. Because a node's halo always fits inside its own block, sibling
 * subtrees — leaves or internal nodes — never overlap regardless of label width.
 * Depth sets the row; the SVG scrolls when a tree is wide.
 */
export function layoutCStructure(cstruct: CStructure): TreeLayout {
  const { root, nodes } = cstruct;
  const placed = new Map<string, { x: number; depth: number }>();
  const edges: LaidOutEdge[] = [];
  let maxDepth = 0;

  const widthOf = (id: string) => labelWidth(displayLabel(nodes[id]?.label ?? ""));

  // Block width: max of this node's own label width and its children's span.
  const blockMemo = new Map<string, number>();
  const blockWidth = (id: string): number => {
    const cached = blockMemo.get(id);
    if (cached !== undefined) return cached;
    const children = nodes[id]?.children ?? [];
    let width = widthOf(id);
    if (children.length > 0) {
      const span =
        children.reduce((sum, childId) => sum + blockWidth(childId), 0) +
        SIBLING_GAP * (children.length - 1);
      width = Math.max(width, span);
    }
    blockMemo.set(id, width);
    return width;
  };

  // Place a subtree within [blockLeft, blockLeft + blockWidth(id)] and return the
  // node's centre x. Children are centred as a group; the node sits over the
  // midpoint of its first and last child's centres (classic tidy-tree look).
  const place = (id: string, blockLeft: number, depth: number): number => {
    const node = nodes[id];
    // Defensive: the serializer never emits a dangling child ref.
    if (!node) return blockLeft;
    if (depth > maxDepth) maxDepth = depth;
    const children = node.children ?? [];
    let center: number;
    if (children.length === 0) {
      center = blockLeft + widthOf(id) / 2;
    } else {
      const span =
        children.reduce((sum, childId) => sum + blockWidth(childId), 0) +
        SIBLING_GAP * (children.length - 1);
      let cursor = blockLeft + (blockWidth(id) - span) / 2;
      const childCenters: number[] = [];
      for (const childId of children) {
        edges.push({ from: id, to: childId });
        childCenters.push(place(childId, cursor, depth + 1));
        cursor += blockWidth(childId) + SIBLING_GAP;
      }
      center = (childCenters[0] + childCenters[childCenters.length - 1]) / 2;
    }
    placed.set(id, { x: center, depth });
    return center;
  };

  if (nodes[root]) place(root, TREE_PAD, 0);

  const laidOut: LaidOutNode[] = [];
  for (const [id, { x, depth }] of placed) {
    const node = nodes[id];
    laidOut.push({
      id,
      label: node.label,
      equations: node.equations ?? [],
      gloss: node.gloss ?? null,
      x,
      y: TREE_PAD + depth * NODE_Y_GAP,
    });
  }

  const width = TREE_PAD * 2 + (nodes[root] ? blockWidth(root) : 0);
  const height = TREE_PAD * 2 + maxDepth * NODE_Y_GAP + NODE_Y_GAP;
  return { nodes: laidOut, edges, width, height };
}
