// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ParseResponse } from "../api/client";
import { CFStructureView } from "./CFStructureView";

// S(c0) → [ NP(c1), V(c2) ]. φ: the matrix S and its head V project f0; the
// subject NP projects f1 (= f0.SUBJ).
const RESULT: ParseResponse = {
  text: "Kumain ang bata.",
  parses: [
    {
      id: "p0",
      c_structure: {
        root: "c0",
        nodes: {
          c0: { id: "c0", label: "S", children: ["c1", "c2"] },
          c1: { id: "c1", label: "NP", children: [] },
          c2: { id: "c2", label: "V", children: [] },
        },
      },
      f_structure: {
        root: "f0",
        nodes: {
          f0: { id: "f0", feats: { PRED: "kain", SUBJ: { $ref: "f1" } } },
          f1: { id: "f1", feats: { PRED: "bata" } },
        },
      },
      a_structure: { pred: "KAIN", roles: ["agent"], mapping: { agent: "SUBJ" } },
      diagnostics: [],
      correspondence: { c0: "f0", c2: "f0", c1: "f1" },
    },
  ],
  fragments: [],
  meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
};

describe("CFStructureView", () => {
  it("renders both projection panels", () => {
    render(<CFStructureView result={RESULT} selected={0} />);
    expect(screen.getByText("C-structure")).toBeInTheDocument();
    expect(screen.getByText("F-structure")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /c-structure tree/i })).toBeInTheDocument();
    expect(screen.getByText("kain")).toBeInTheDocument();
  });

  it("hovering a c-node lights its f-node and every co-projecting c-node", () => {
    const { container } = render(<CFStructureView result={RESULT} selected={0} />);
    // V (c2) projects f0; so do the matrix S (c0). The NP (c1) projects f1.
    fireEvent.mouseOver(screen.getByText("V"));
    expect(screen.getByText("V")).toHaveClass("fill-amber-800");
    expect(screen.getByText("S")).toHaveClass("fill-amber-800");
    expect(screen.getByText("NP")).not.toHaveClass("fill-amber-800");
    expect(container.querySelector('[data-fs-node="f0"]')).toHaveClass("bg-amber-50");
    expect(container.querySelector('[data-fs-node="f1"]')).not.toHaveClass("bg-amber-50");
  });

  it("hovering an f-node lights the c-nodes that project to it", () => {
    const { container } = render(<CFStructureView result={RESULT} selected={0} />);
    const subj = container.querySelector('[data-fs-node="f1"]');
    expect(subj).not.toBeNull();
    fireEvent.mouseOver(subj!);
    // f1 is projected by the NP (c1) only.
    expect(screen.getByText("NP")).toHaveClass("fill-amber-800");
    expect(screen.getByText("S")).not.toHaveClass("fill-amber-800");
    expect(screen.getByText("V")).not.toHaveClass("fill-amber-800");
    expect(subj).toHaveClass("bg-amber-50");
  });
});
