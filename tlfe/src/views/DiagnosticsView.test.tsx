// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { DiagnosticModel, ParseResponse } from "../api/client";
import { DiagnosticsView } from "./DiagnosticsView";

function resultWith(diagnostics: DiagnosticModel[]): ParseResponse {
  return {
    text: "Kumain ang.",
    parses: [
      {
        id: "p0",
        c_structure: {
          root: "c0",
          nodes: { c0: { id: "c0", label: "S", children: [] } },
        },
        f_structure: { root: "f0", nodes: { f0: { id: "f0", feats: {} } } },
        a_structure: { pred: "x", roles: [], mapping: {} },
        diagnostics,
      },
    ],
    fragments: [],
    meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
  };
}

describe("DiagnosticsView", () => {
  it("prompts when there is no result", () => {
    render(<DiagnosticsView result={undefined} selected={0} />);
    expect(screen.getByText(/parse a sentence to see diagnostics/i)).toBeInTheDocument();
  });

  it("says so when the selected parse has no diagnostics", () => {
    render(<DiagnosticsView result={resultWith([])} selected={0} />);
    expect(screen.getByText(/no diagnostics for parse 1/i)).toBeInTheDocument();
  });

  it("renders kind, message, blocking badge, and the c-node anchor", () => {
    const result = resultWith([
      {
        id: "d0",
        kind: "completeness-failed",
        message: "SUBJ required",
        cnode_label: "S -> NP VP",
        equation: "(↑ SUBJ)",
        path: ["SUBJ"],
        blocking: true,
      },
    ]);
    render(<DiagnosticsView result={result} selected={0} />);
    expect(screen.getByText("completeness-failed")).toBeInTheDocument();
    expect(screen.getByText("SUBJ required")).toBeInTheDocument();
    expect(screen.getByText("blocking")).toBeInTheDocument();
    expect(screen.getByText("S -> NP VP")).toBeInTheDocument();
  });

  it("shows fragment diagnostics when there is no complete parse", () => {
    const result: ParseResponse = {
      text: "Kumain ang.",
      parses: [],
      fragments: [
        {
          span: [0, 2],
          c_structure: {
            root: "c0",
            nodes: { c0: { id: "c0", label: "NP", children: [] } },
          },
          f_structure: { root: "f0", nodes: { f0: { id: "f0", feats: {} } } },
          a_structure: { pred: "y", roles: [], mapping: {} },
          diagnostics: [{ id: "d0", kind: "incomplete", message: "dangling", blocking: false }],
        },
      ],
      meta: { n_best: 5, parse_count: 0, fragment_count: 1 },
    };
    render(<DiagnosticsView result={result} selected={0} />);
    expect(screen.getByText(/fragment \[0, 2\]/i)).toBeInTheDocument();
    expect(screen.getByText("dangling")).toBeInTheDocument();
  });
});
