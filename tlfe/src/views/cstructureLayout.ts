// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import type { CStructure } from "../api/client";

export interface LaidOutNode {
  id: string;
  label: string;
  equations: string[];
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

// Tidy-tree spacing (px). Leaves take evenly-spaced columns; each parent is
// centred over its children; depth drives the row.
export const NODE_X_GAP = 96;
export const NODE_Y_GAP = 84;
export const TREE_PAD = 36;

/**
 * Lay out a c-structure node table as a tidy tree in a single bottom-up pass:
 * leaves take successive columns, internal nodes centre over their children,
 * depth sets the row. No contour threading — good enough for parse trees; the
 * SVG scrolls when a tree is wide.
 */
export function layoutCStructure(cstruct: CStructure): TreeLayout {
  const { root, nodes } = cstruct;
  const placed = new Map<string, { col: number; depth: number }>();
  const edges: LaidOutEdge[] = [];
  let nextLeafCol = 0;
  let maxDepth = 0;

  const visit = (id: string, depth: number): number => {
    const node = nodes[id];
    // Defensive: the serializer never emits a dangling child ref, but never
    // recurse into a missing node.
    if (!node) return nextLeafCol;
    if (depth > maxDepth) maxDepth = depth;
    const children = node.children ?? [];
    let col: number;
    if (children.length === 0) {
      col = nextLeafCol;
      nextLeafCol += 1;
    } else {
      const childCols = children.map((childId) => {
        edges.push({ from: id, to: childId });
        return visit(childId, depth + 1);
      });
      col = (childCols[0] + childCols[childCols.length - 1]) / 2;
    }
    placed.set(id, { col, depth });
    return col;
  };

  if (nodes[root]) visit(root, 0);

  const laidOut: LaidOutNode[] = [];
  for (const [id, { col, depth }] of placed) {
    const node = nodes[id];
    laidOut.push({
      id,
      label: node.label,
      equations: node.equations ?? [],
      x: TREE_PAD + col * NODE_X_GAP,
      y: TREE_PAD + depth * NODE_Y_GAP,
    });
  }

  const leafSpan = Math.max(nextLeafCol - 1, 0);
  const width = TREE_PAD * 2 + leafSpan * NODE_X_GAP + NODE_X_GAP;
  const height = TREE_PAD * 2 + maxDepth * NODE_Y_GAP + NODE_Y_GAP;
  return { nodes: laidOut, edges, width, height };
}
