// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App.tsx";

describe("App", () => {
  it("renders the inspector heading", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /tgllfg inspector/i })).toBeInTheDocument();
  });

  it("renders the three parse-view tabs", () => {
    render(<App />);
    expect(screen.getByRole("tab", { name: "C-structure" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "F-structure" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "JSON" })).toBeInTheDocument();
  });
});
