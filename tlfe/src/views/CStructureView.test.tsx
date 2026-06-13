// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ParseResponse } from "../api/client";
import { CStructureView } from "./CStructureView";

const RESULT: ParseResponse = {
  text: "Kumain ang bata.",
  parses: [
    {
      id: "p0",
      c_structure: {
        root: "c0",
        nodes: {
          c0: { id: "c0", label: "S", children: ["c1"], equations: ["(↑ SUBJ) = ↓"] },
          c1: { id: "c1", label: "V", children: [], equations: ["(↑ PRED) = 'KAIN'"] },
        },
      },
      f_structure: { root: "f0", nodes: { f0: { id: "f0", feats: {} } } },
      a_structure: { pred: "KAIN", roles: [], mapping: {} },
      diagnostics: [],
    },
  ],
  fragments: [],
  meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
};

describe("CStructureView", () => {
  it("prompts when there is no result", () => {
    render(<CStructureView result={undefined} selected={0} />);
    expect(screen.getByText(/parse a sentence to see its c-structure/i)).toBeInTheDocument();
  });

  it("renders the node labels of the selected parse", () => {
    render(<CStructureView result={RESULT} selected={0} />);
    expect(screen.getByText("S")).toBeInTheDocument();
    expect(screen.getByText("V")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /c-structure tree/i })).toBeInTheDocument();
  });

  it("reports a fragment-only result", () => {
    const fragmentsOnly: ParseResponse = {
      ...RESULT,
      parses: [],
      meta: { n_best: 5, parse_count: 0, fragment_count: 2 },
    };
    render(<CStructureView result={fragmentsOnly} selected={0} />);
    expect(screen.getByText(/no complete parse/i)).toBeInTheDocument();
    expect(screen.getByText(/2 fragments/i)).toBeInTheDocument();
  });

  it("keeps equations out of the tree until a node is clicked, then shows them", async () => {
    render(<CStructureView result={RESULT} selected={0} />);
    // Label-only by default — the functional equations are not drawn inline.
    expect(screen.queryByText("(↑ PRED) = 'KAIN'")).not.toBeInTheDocument();
    // Clicking a node opens a popover listing its equations.
    fireEvent.click(screen.getByText("V"));
    expect(await screen.findByText("(↑ PRED) = 'KAIN'")).toBeInTheDocument();
  });
});
