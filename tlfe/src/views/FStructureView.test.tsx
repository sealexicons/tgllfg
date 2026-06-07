// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ParseResponse } from "../api/client";
import { FStructureView } from "./FStructureView";

// f0 (root): PRED "want", SUBJ → f1, XCOMP → f2
// f1: PRED "Maria"   (referenced by f0.SUBJ and f2.SUBJ → reentrant)
// f2: PRED "leave", SUBJ → f1
const RESULT: ParseResponse = {
  text: "Gusto ni Maria umalis.",
  parses: [
    {
      id: "p0",
      c_structure: {
        root: "c0",
        nodes: { c0: { id: "c0", label: "S", children: [] } },
      },
      f_structure: {
        root: "f0",
        nodes: {
          f0: {
            id: "f0",
            feats: { PRED: "want", SUBJ: { $ref: "f1" }, XCOMP: { $ref: "f2" } },
          },
          f1: { id: "f1", feats: { PRED: "Maria" } },
          f2: { id: "f2", feats: { PRED: "leave", SUBJ: { $ref: "f1" } } },
        },
      },
      a_structure: { pred: "WANT", roles: [], mapping: {} },
      diagnostics: [],
    },
  ],
  fragments: [],
  meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
};

describe("FStructureView", () => {
  it("prompts when there is no result", () => {
    render(<FStructureView result={undefined} selected={0} />);
    expect(screen.getByText(/parse a sentence to see its f-structure/i)).toBeInTheDocument();
  });

  it("renders scalar feats, attribute names, and inline-expanded refs", () => {
    render(<FStructureView result={RESULT} selected={0} />);
    expect(screen.getByText("want")).toBeInTheDocument();
    expect(screen.getByText("XCOMP")).toBeInTheDocument();
    // f1 expands inline under f0.SUBJ, so its PRED shows once.
    expect(screen.getByText("Maria")).toBeInTheDocument();
    expect(screen.getByText("leave")).toBeInTheDocument();
  });

  it("tags a reentrant node at every occurrence and cross-highlights on hover", () => {
    const { container } = render(<FStructureView result={RESULT} selected={0} />);
    const tags = container.querySelectorAll('[data-fs-id="f1"]');
    expect(tags).toHaveLength(2); // expansion tag + the chip under f2.SUBJ
    fireEvent.mouseOver(tags[0]);
    const lit = container.querySelectorAll('[data-fs-id="f1"].bg-amber-200');
    expect(lit).toHaveLength(2);
  });

  it("reports a fragment-only result", () => {
    const fragmentsOnly: ParseResponse = {
      ...RESULT,
      parses: [],
      meta: { n_best: 5, parse_count: 0, fragment_count: 3 },
    };
    render(<FStructureView result={fragmentsOnly} selected={0} />);
    expect(screen.getByText(/no complete parse/i)).toBeInTheDocument();
    expect(screen.getByText(/3 fragments/i)).toBeInTheDocument();
  });
});
