// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ParseResponse } from "../api/client";
import { AStructureView } from "./AStructureView";

const RESULT: ParseResponse = {
  text: "Kumain ang bata ng kanin.",
  parses: [
    {
      id: "p0",
      c_structure: {
        root: "c0",
        nodes: { c0: { id: "c0", label: "S", children: [] } },
      },
      f_structure: { root: "f0", nodes: { f0: { id: "f0", feats: {} } } },
      a_structure: {
        pred: "kain",
        roles: ["agent", "patient"],
        mapping: { agent: "SUBJ", patient: "OBJ" },
      },
      diagnostics: [],
    },
  ],
  fragments: [],
  meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
};

describe("AStructureView", () => {
  it("prompts when there is no result", () => {
    render(<AStructureView result={undefined} selected={0} />);
    expect(screen.getByText(/parse a sentence to see its a-structure/i)).toBeInTheDocument();
  });

  it("renders the predicate and the role→GF mapping", () => {
    render(<AStructureView result={RESULT} selected={0} />);
    expect(screen.getByText("kain")).toBeInTheDocument();
    expect(screen.getByText("agent")).toBeInTheDocument();
    expect(screen.getByText("patient")).toBeInTheDocument();
    expect(screen.getByText(/SUBJ/)).toBeInTheDocument();
    expect(screen.getByText(/OBJ/)).toBeInTheDocument();
  });

  it("reports a fragment-only result", () => {
    const fragmentsOnly: ParseResponse = {
      ...RESULT,
      parses: [],
      meta: { n_best: 5, parse_count: 0, fragment_count: 1 },
    };
    render(<AStructureView result={fragmentsOnly} selected={0} />);
    expect(screen.getByText(/no complete parse/i)).toBeInTheDocument();
  });
});
