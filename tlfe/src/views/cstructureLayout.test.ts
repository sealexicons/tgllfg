// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { describe, expect, it } from "vitest";

import type { CStructure } from "../api/client";
import { displayLabel, labelWidth, layoutCStructure } from "./cstructureLayout";

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

  it("orders leaves left to right and centres parents over children", () => {
    const layout = layoutCStructure(SAMPLE);
    const byId = new Map(layout.nodes.map((node) => [node.id, node]));
    // Leaves NP then V, left to right.
    expect(byId.get("c1")!.x).toBeLessThan(byId.get("c3")!.x);
    // VP sits over its single leaf V.
    expect(byId.get("c2")!.x).toBe(byId.get("c3")!.x);
    // S is centred between its children NP and VP.
    expect(byId.get("c0")!.x).toBe((byId.get("c1")!.x + byId.get("c2")!.x) / 2);
  });

  it("reserves horizontal room for wide labels so siblings never overlap", () => {
    const wide: CStructure = {
      root: "r",
      nodes: {
        r: { id: "r", label: "S", children: ["a", "b"], equations: [] },
        a: { id: "a", label: "PUNCT[PUNCT_CLASS=COMMA]", children: [], equations: [] },
        b: { id: "b", label: "NP[COORD=AND]", children: [], equations: [] },
      },
    };
    const layout = layoutCStructure(wide);
    const byId = new Map(layout.nodes.map((node) => [node.id, node]));
    const a = byId.get("a")!;
    const b = byId.get("b")!;
    const clearance = labelWidth(displayLabel(a.label)) / 2 + labelWidth(displayLabel(b.label)) / 2;
    // The two halos clear each other: centres at least their half-widths apart.
    expect(Math.abs(b.x - a.x)).toBeGreaterThanOrEqual(clearance);
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
