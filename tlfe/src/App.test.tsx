// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import App from "./App.tsx";

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
});
