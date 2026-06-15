// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ParseResponse } from "../api/client";
import { CStructureView } from "./CStructureView";

// The context-menu gloss pulls from /lex/search via useLexSearch; stub it so the
// gloss assertion is deterministic and DB-free.
vi.mock("../api/hooks", () => ({
  useLexSearch: () => ({
    data: { matches: [{ id: "1", citation_form: "kain", pos: "v", gloss: "to eat", score: 1 }] },
    isLoading: false,
    isError: false,
  }),
}));

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

  it("abbreviates a true binary feature in the label, keeping enum values", () => {
    const withFeat: ParseResponse = {
      text: "x",
      parses: [
        {
          id: "p0",
          c_structure: {
            root: "c0",
            nodes: {
              c0: { id: "c0", label: "NP[CASE=NOM]", children: ["c1"], equations: [] },
              c1: { id: "c1", label: "N[N_CORE=True]", children: [], equations: [] },
            },
          },
          f_structure: { root: "f0", nodes: { f0: { id: "f0", feats: {} } } },
          a_structure: { pred: "X", roles: [], mapping: {} },
          diagnostics: [],
        },
      ],
      fragments: [],
      meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
    };
    render(<CStructureView result={withFeat} selected={0} />);
    expect(screen.getByText("N[N_CORE]")).toBeInTheDocument();
    expect(screen.queryByText("N[N_CORE=True]")).not.toBeInTheDocument();
    expect(screen.getByText("NP[CASE=NOM]")).toBeInTheDocument();
  });

  it("offers a clickable φ-link in the equation popover (post-10)", async () => {
    const onSelectFNode = vi.fn();
    render(
      <CStructureView
        result={RESULT}
        selected={0}
        correspondence={{ c1: "f9" }}
        onSelectFNode={onSelectFNode}
      />,
    );
    fireEvent.click(screen.getByText("V")); // open c1's equation popover
    fireEvent.click(await screen.findByRole("button", { name: /f9/ }));
    expect(onSelectFNode).toHaveBeenCalledWith("f9");
  });

  it("opens a context menu with Show φ on right-click (post-10)", async () => {
    const onSelectFNode = vi.fn();
    render(
      <CStructureView
        result={RESULT}
        selected={0}
        correspondence={{ c1: "f9" }}
        onSelectFNode={onSelectFNode}
      />,
    );
    fireEvent.contextMenu(screen.getByText("V"));
    fireEvent.click(await screen.findByRole("menuitem", { name: /Show φ/ }));
    expect(onSelectFNode).toHaveBeenCalledWith("f9");
  });

  it("shows a terminal's gloss in the context menu (post-10)", async () => {
    const withLemma: ParseResponse = {
      text: "Kumain ang bata.",
      parses: [
        {
          id: "p0",
          c_structure: {
            root: "c0",
            nodes: {
              c0: { id: "c0", label: "S", children: ["c1"], equations: [] },
              c1: { id: "c1", label: "V", children: [], equations: ["(↑ LEMMA) = 'kain'"] },
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
    render(<CStructureView result={withLemma} selected={0} />);
    fireEvent.contextMenu(screen.getByText("V"));
    expect(await screen.findByText("to eat")).toBeInTheDocument();
  });
});
