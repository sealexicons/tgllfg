// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

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

  it("orders attributes canonically and hides valueless feats", () => {
    const result: ParseResponse = {
      text: "x",
      parses: [
        {
          id: "p0",
          c_structure: { root: "c0", nodes: { c0: { id: "c0", label: "S", children: [] } } },
          f_structure: {
            root: "f0",
            nodes: {
              f0: {
                id: "f0",
                feats: { LEMMA: "x", CASE: "NOM", PRED: "p", ADJUNCT: [], INTENS: { $ref: "f1" } },
              },
              f1: { id: "f1", feats: {} },
            },
          },
          a_structure: { pred: "X", roles: [], mapping: {} },
          diagnostics: [],
        },
      ],
      fragments: [],
      meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
    };
    const { container } = render(<FStructureView result={result} selected={0} />);
    const text = container.textContent ?? "";
    // Canonical order: PRED first, CASE (nominal feat) next, LEMMA last.
    expect(text.indexOf("PRED")).toBeLessThan(text.indexOf("CASE"));
    expect(text.indexOf("CASE")).toBeLessThan(text.indexOf("LEMMA"));
    // The empty-set ADJUNCT and the ref to the empty node f1 are both valueless.
    expect(text).not.toContain("ADJUNCT");
    expect(text).not.toContain("INTENS");
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

  it("opens a sub-structure popover when a reentrancy tag is clicked", async () => {
    const { container } = render(<FStructureView result={RESULT} selected={0} />);
    fireEvent.click(container.querySelector('[data-fs-id="f1"]')!);
    const dialog = await screen.findByRole("dialog");
    // The popover shows f1's own AVM (PRED Maria).
    expect(within(dialog).getByText("PRED")).toBeInTheDocument();
    expect(within(dialog).getByText("Maria")).toBeInTheDocument();
  });

  it("reports the clicked f-node id via onSelectNode", () => {
    const onSelectNode = vi.fn();
    const { container } = render(
      <FStructureView result={RESULT} selected={0} onSelectNode={onSelectNode} />,
    );
    fireEvent.click(container.querySelector('[data-fs-id="f1"]')!);
    expect(onSelectNode).toHaveBeenCalledWith("f1");
  });

  it("makes a singly-referenced scalar ref clickable (post-10)", () => {
    // f0.SUBJ → f1 referenced exactly once: previously inline-only (no chip),
    // now a chip so the scalar GF is selectable / openable like any other node.
    const result: ParseResponse = {
      text: "x",
      parses: [
        {
          id: "p0",
          c_structure: { root: "c0", nodes: { c0: { id: "c0", label: "S", children: [] } } },
          f_structure: {
            root: "f0",
            nodes: {
              f0: { id: "f0", feats: { PRED: "sleep", SUBJ: { $ref: "f1" } } },
              f1: { id: "f1", feats: { PRED: "bata" } },
            },
          },
          a_structure: { pred: "SLEEP", roles: [], mapping: {} },
          diagnostics: [],
        },
      ],
      fragments: [],
      meta: { n_best: 5, parse_count: 1, fragment_count: 0 },
    };
    const onSelectNode = vi.fn();
    const { container } = render(
      <FStructureView result={result} selected={0} onSelectNode={onSelectNode} />,
    );
    const chip = container.querySelector('[data-fs-id="f1"]');
    expect(chip).not.toBeNull();
    // It still expands inline (PRED bata shown below the chip).
    expect(screen.getByText("bata")).toBeInTheDocument();
    fireEvent.click(chip!);
    expect(onSelectNode).toHaveBeenCalledWith("f1");
  });

  it("scrolls the AVM to an f-node when scrollTo is set (post-10)", () => {
    const scrollIntoView = vi.spyOn(Element.prototype, "scrollIntoView");
    render(<FStructureView result={RESULT} selected={0} scrollTo={{ fid: "f1", nonce: 1 }} />);
    expect(scrollIntoView).toHaveBeenCalled();
    scrollIntoView.mockRestore();
  });
});
