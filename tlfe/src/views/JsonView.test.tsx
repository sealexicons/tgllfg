// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ParseResponse } from "../api/client";
import { JsonView } from "./JsonView";

const RESULT: ParseResponse = {
  text: "Kumain ang bata.",
  parses: [],
  fragments: [],
  meta: { n_best: 5, parse_count: 0, fragment_count: 0 },
};

afterEach(() => {
  vi.restoreAllMocks();
  Reflect.deleteProperty(window, "showSaveFilePicker");
  Reflect.deleteProperty(URL, "createObjectURL");
  Reflect.deleteProperty(URL, "revokeObjectURL");
  Reflect.deleteProperty(navigator, "clipboard");
});

describe("JsonView", () => {
  it("prompts when there is no result", () => {
    render(<JsonView result={undefined} />);
    expect(screen.getByText(/parse a sentence to see the raw payload/i)).toBeInTheDocument();
  });

  it("renders the full ParseResponse payload", () => {
    const { container } = render(<JsonView result={RESULT} />);
    expect(container.querySelector("pre")?.textContent).toBe(JSON.stringify(RESULT, null, 2));
  });

  it("copies the JSON payload to the clipboard and shows a confirmation snackbar", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    render(<JsonView result={RESULT} />);
    fireEvent.click(screen.getByRole("button", { name: /copy json/i }));
    expect(writeText).toHaveBeenCalledWith(JSON.stringify(RESULT, null, 2));
    expect(await screen.findByText(/copied json/i)).toBeInTheDocument();
  });

  it("blurs the Copy button after a mouse click but keeps focus for keyboard use", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    render(<JsonView result={RESULT} />);
    const button = screen.getByRole("button", { name: /copy json/i });

    // Keyboard activation (detail 0) leaves focus in place.
    button.focus();
    fireEvent.click(button, { detail: 0 });
    expect(await screen.findByText(/copied json/i)).toBeInTheDocument();
    expect(button).toHaveFocus();

    // A mouse click (detail > 0) blurs it so the focus ring doesn't linger.
    fireEvent.click(button, { detail: 1 });
    await waitFor(() => expect(button).not.toHaveFocus());
  });

  it("saves through the native Save As picker when available", async () => {
    const write = vi.fn().mockResolvedValue(undefined);
    const close = vi.fn().mockResolvedValue(undefined);
    const createWritable = vi.fn().mockResolvedValue({ write, close });
    const showSaveFilePicker = vi.fn().mockResolvedValue({ createWritable });
    Object.defineProperty(window, "showSaveFilePicker", {
      value: showSaveFilePicker,
      configurable: true,
    });

    render(<JsonView result={RESULT} />);
    fireEvent.click(screen.getByRole("button", { name: /save json/i }));

    await waitFor(() => expect(close).toHaveBeenCalledOnce());
    // Defaults the dialog to our suggested name; the user can still change it.
    expect(showSaveFilePicker).toHaveBeenCalledWith(
      expect.objectContaining({
        suggestedName: expect.stringMatching(/^tgllfg-parse-\d{15}\.json$/),
      }),
    );
    expect(write).toHaveBeenCalledOnce();
    expect(await screen.findByText(/saved json/i)).toBeInTheDocument();
  });

  it("blurs the button after a mouse-driven save so the focus tooltip can't reopen", async () => {
    const createWritable = vi.fn().mockResolvedValue({
      write: vi.fn().mockResolvedValue(undefined),
      close: vi.fn().mockResolvedValue(undefined),
    });
    const showSaveFilePicker = vi.fn().mockResolvedValue({ createWritable });
    Object.defineProperty(window, "showSaveFilePicker", {
      value: showSaveFilePicker,
      configurable: true,
    });

    render(<JsonView result={RESULT} />);
    const button = screen.getByRole("button", { name: /save json/i });
    button.focus();
    expect(button).toHaveFocus();
    // detail > 0 marks a pointer (mouse) click; the Save dialog returns focus
    // here on close, which must not be allowed to re-open the tooltip.
    fireEvent.click(button, { detail: 1 });

    expect(await screen.findByText(/saved json/i)).toBeInTheDocument();
    await waitFor(() => expect(button).not.toHaveFocus());
  });

  it("falls back to a direct download when the Save As picker is unavailable", () => {
    const createObjectURL = vi.fn(() => "blob:mock");
    const revokeObjectURL = vi.fn();
    Object.assign(URL, { createObjectURL, revokeObjectURL });
    let name = "";
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      name = this.download;
    });

    render(<JsonView result={RESULT} />);
    fireEvent.click(screen.getByRole("button", { name: /save json/i }));

    expect(createObjectURL).toHaveBeenCalledOnce();
    // YYMMDDhhmmssuuu — 15 digits, millisecond precision.
    expect(name).toMatch(/^tgllfg-parse-\d{15}\.json$/);
    expect(screen.getByText(/saved json/i)).toBeInTheDocument();
    // The blob URL survives until page unload, so a slow or interrupted Save
    // dialog can never have the file truncated out from under it.
    expect(revokeObjectURL).not.toHaveBeenCalled();
    window.dispatchEvent(new Event("pagehide"));
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:mock");
  });
});
