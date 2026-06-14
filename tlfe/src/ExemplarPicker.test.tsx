// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { act, fireEvent, render, renderHook, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ExemplarsResponse } from "./api/client";
import { ExemplarPicker } from "./ExemplarPicker";
import { useExemplarPicker, type ExemplarPickerState } from "./useExemplarPicker";

// wave1: A=[s1,s2], B=[s1]; wave2: C=[s1]. Flat order: a-s1, a-s2, b-s1, c-s1.
const FIXTURE: ExemplarsResponse = {
  sources: [
    {
      source: "wave1",
      sections: [
        {
          section: "A",
          sentences: [
            { locator: "A/s1", sentence: "s1", text: "a-s1" },
            { locator: "A/s2", sentence: "s2", text: "a-s2" },
          ],
        },
        { section: "B", sentences: [{ locator: "B/s1", sentence: "s1", text: "b-s1" }] },
      ],
    },
    {
      source: "wave2",
      sections: [{ section: "C", sentences: [{ locator: "C/s1", sentence: "s1", text: "c-s1" }] }],
    },
  ],
};

vi.mock("./api/hooks", () => ({
  useExemplars: () => ({ data: FIXTURE, isLoading: false }),
}));

describe("useExemplarPicker", () => {
  it("does not populate the field while disabled", () => {
    const onPick = vi.fn();
    renderHook(() => useExemplarPicker(false, onPick));
    expect(onPick).not.toHaveBeenCalled();
  });

  it("auto-syncs the first exemplar when enabled", () => {
    const onPick = vi.fn();
    const { result } = renderHook(() => useExemplarPicker(true, onPick));
    expect(onPick).toHaveBeenCalledWith("a-s1");
    expect([
      result.current.sourceIdx,
      result.current.sectionIdx,
      result.current.sentenceIdx,
    ]).toEqual([0, 0, 0]);
    expect(result.current.ready).toBe(true);
  });

  it("steps forward across sections and sources, then wraps to the start", () => {
    const onPick = vi.fn();
    const { result } = renderHook(() => useExemplarPicker(true, onPick)); // auto-synced a-s1
    act(() => result.current.step(1)); // → a-s2
    expect(onPick).toHaveBeenLastCalledWith("a-s2");
    act(() => result.current.step(1)); // → b-s1 (next section)
    expect(onPick).toHaveBeenLastCalledWith("b-s1");
    act(() => result.current.step(1)); // → c-s1 (next source)
    expect(onPick).toHaveBeenLastCalledWith("c-s1");
    expect(result.current.sourceIdx).toBe(1);
    act(() => result.current.step(1)); // wrap → a-s1
    expect(onPick).toHaveBeenLastCalledWith("a-s1");
    expect([result.current.sourceIdx, result.current.sentenceIdx]).toEqual([0, 0]);
  });

  it("steps backward from the first, wrapping to the last", () => {
    const onPick = vi.fn();
    const { result } = renderHook(() => useExemplarPicker(true, onPick));
    act(() => result.current.step(-1)); // a-s1 → wrap → c-s1
    expect(onPick).toHaveBeenLastCalledWith("c-s1");
  });

  it("dropdown selects jump to the right leaf and populate", () => {
    const onPick = vi.fn();
    const { result } = renderHook(() => useExemplarPicker(true, onPick));
    act(() => result.current.selectSource(1));
    expect(onPick).toHaveBeenLastCalledWith("c-s1");
    expect(result.current.sourceIdx).toBe(1);
    act(() => result.current.selectSource(0));
    act(() => result.current.selectSection(1));
    expect(onPick).toHaveBeenLastCalledWith("b-s1");
    expect([result.current.sectionIdx, result.current.sentenceIdx]).toEqual([1, 0]);
  });
});

describe("ExemplarPicker", () => {
  const ready: ExemplarPickerState = {
    sources: FIXTURE.sources,
    ready: true,
    isLoading: false,
    sourceIdx: 0,
    sectionIdx: 0,
    sentenceIdx: 0,
    selectSource: vi.fn(),
    selectSection: vi.fn(),
    selectSentence: vi.fn(),
    step: vi.fn(),
  };

  it("renders the three cascading dropdowns and the step hint", () => {
    render(<ExemplarPicker picker={ready} />);
    expect(screen.getByText("source:")).toBeInTheDocument();
    expect(screen.getByText("section:")).toBeInTheDocument();
    expect(screen.getByText("sentence:")).toBeInTheDocument();
    expect(screen.getByText(/ctrl\+↑\/↓ to step/i)).toBeInTheDocument();
    // Current labels render directly in the triggers (lowercased).
    expect(screen.getByText("wave1")).toBeInTheDocument();
  });

  it("shows a loading state", () => {
    render(<ExemplarPicker picker={{ ...ready, isLoading: true }} />);
    expect(screen.getByText(/loading exemplars/i)).toBeInTheDocument();
  });

  it("shows an empty state", () => {
    render(<ExemplarPicker picker={{ ...ready, ready: false }} />);
    expect(screen.getByText(/no exemplars available/i)).toBeInTheDocument();
  });

  it("steps on Ctrl/Meta+arrow at a trigger instead of opening the dropdown", () => {
    const stepper = { ...ready, step: vi.fn() };
    render(<ExemplarPicker picker={stepper} />);
    const trigger = screen.getByRole("combobox", { name: "source" });
    fireEvent.keyDown(trigger, { key: "ArrowDown", ctrlKey: true });
    expect(stepper.step).toHaveBeenCalledWith(1);
    fireEvent.keyDown(trigger, { key: "ArrowUp", metaKey: true });
    expect(stepper.step).toHaveBeenLastCalledWith(-1);
    // A plain arrow is left to Radix (opens the dropdown), not treated as a step.
    fireEvent.keyDown(trigger, { key: "ArrowDown" });
    expect(stepper.step).toHaveBeenCalledTimes(2);
  });
});
