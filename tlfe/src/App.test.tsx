// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import App from "./App.tsx";

// Stub the parse mutation so submitting (to seed input history) never hits the
// network; the views render their idle states with data undefined.
vi.mock("./api/hooks", () => ({
  useParse: () => ({
    mutate: vi.fn(),
    isPending: false,
    isError: false,
    error: null,
    data: undefined,
  }),
}));

function renderApp() {
  const queryClient = new QueryClient();
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return render(<App />, { wrapper });
}

describe("App", () => {
  it("renders the inspector heading", () => {
    renderApp();
    expect(screen.getByRole("heading", { name: /tgllfg inspector/i })).toBeInTheDocument();
  });

  it("renders the parse-view tabs", () => {
    renderApp();
    expect(screen.getByRole("tab", { name: "C / F" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "A-structure" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Diagnostics" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "JSON" })).toBeInTheDocument();
  });

  it("shows the idle hint before parsing", () => {
    renderApp();
    expect(screen.getByText(/enter a tagalog sentence and press parse/i)).toBeInTheDocument();
  });

  it("disables Parse for empty input and enables it after typing", () => {
    renderApp();
    const button = screen.getByRole("button", { name: "Parse" });
    expect(button).toBeDisabled();
    fireEvent.change(screen.getByRole("textbox", { name: /tagalog sentence/i }), {
      target: { value: "Kumain ang bata." },
    });
    expect(button).toBeEnabled();
  });

  it("accepts the placeholder on Tab when the field is empty", () => {
    renderApp();
    const input = screen.getByRole("textbox", { name: /tagalog sentence/i }) as HTMLInputElement;
    expect(input.value).toBe("");
    fireEvent.keyDown(input, { key: "Tab" });
    expect(input.value).toBe("Bumili ng aklat ang bata.");
  });

  it("walks session input history with ArrowUp / ArrowDown", () => {
    renderApp();
    const input = screen.getByRole("textbox", { name: /tagalog sentence/i }) as HTMLInputElement;
    const form = input.closest("form")!;
    fireEvent.change(input, { target: { value: "Kumain ang bata." } });
    fireEvent.submit(form);
    fireEvent.change(input, { target: { value: "Natulog ang aso." } });
    fireEvent.submit(form);
    fireEvent.change(input, { target: { value: "" } });

    fireEvent.keyDown(input, { key: "ArrowUp" });
    expect(input.value).toBe("Natulog ang aso.");
    fireEvent.keyDown(input, { key: "ArrowUp" });
    expect(input.value).toBe("Kumain ang bata.");
    fireEvent.keyDown(input, { key: "ArrowDown" });
    expect(input.value).toBe("Natulog ang aso.");
    fireEvent.keyDown(input, { key: "ArrowDown" });
    expect(input.value).toBe("");
  });

  it("steps to the previous entry on the first ArrowUp after submitting", () => {
    renderApp();
    const input = screen.getByRole("textbox", { name: /tagalog sentence/i }) as HTMLInputElement;
    const form = input.closest("form")!;
    fireEvent.change(input, { target: { value: "Kumain ang bata." } });
    fireEvent.submit(form);
    fireEvent.change(input, { target: { value: "Natulog ang aso." } });
    fireEvent.submit(form);
    // Field still shows the just-submitted entry; one ArrowUp recalls the prior.
    expect(input.value).toBe("Natulog ang aso.");
    fireEvent.keyDown(input, { key: "ArrowUp" });
    expect(input.value).toBe("Kumain ang bata.");
  });
});
