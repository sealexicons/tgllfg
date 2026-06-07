// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { describe, expect, it } from "vitest";

import type { CStructure } from "../api/client";
import { layoutCStructure, NODE_X_GAP, TREE_PAD } from "./cstructureLayout";

// S -> [NP, VP]; VP -> [V]. Leaves: NP (c1), V (c3).
const SAMPLE: CStructure = {
  root: "c0",
  nodes: {
    c0: { id: "c0", label: "S", children: ["c1", "c2"], equations: ["↑=↓"] },
    c1: { id: "c1", label: "NP", children: [], equations: ["(↑ SUBJ)=↓"] },
    c2: { id: "c2", label: "VP", children: ["c3"], equations: ["↑=↓"] },
    c3: { id: "c3", label: "V", children: [], equations: [] },
  },
};

describe("layoutCStructure", () => {
  it("places every node once with an edge per parent→child", () => {
    const layout = layoutCStructure(SAMPLE);
    expect(layout.nodes).toHaveLength(4);
    expect(layout.edges).toHaveLength(3);
    expect(layout.edges).toEqual(
      expect.arrayContaining([
        { from: "c0", to: "c1" },
        { from: "c0", to: "c2" },
        { from: "c2", to: "c3" },
      ]),
    );
  });

  it("gives leaves successive columns and centres parents over children", () => {
    const layout = layoutCStructure(SAMPLE);
    const byId = new Map(layout.nodes.map((node) => [node.id, node]));
    // Leaves NP and V take columns 0 and 1.
    expect(byId.get("c1")!.x).toBe(TREE_PAD);
    expect(byId.get("c3")!.x).toBe(TREE_PAD + NODE_X_GAP);
    // VP sits over its single leaf V.
    expect(byId.get("c2")!.x).toBe(byId.get("c3")!.x);
    // S is centred between its children NP and VP.
    expect(byId.get("c0")!.x).toBe((byId.get("c1")!.x + byId.get("c2")!.x) / 2);
  });

  it("increases the row with depth", () => {
    const layout = layoutCStructure(SAMPLE);
    const byId = new Map(layout.nodes.map((node) => [node.id, node]));
    expect(byId.get("c0")!.y).toBeLessThan(byId.get("c1")!.y);
    expect(byId.get("c1")!.y).toBeLessThan(byId.get("c3")!.y);
  });

  it("carries the label and equations through", () => {
    const layout = layoutCStructure(SAMPLE);
    const np = layout.nodes.find((node) => node.id === "c1")!;
    expect(np.label).toBe("NP");
    expect(np.equations).toEqual(["(↑ SUBJ)=↓"]);
  });
});
