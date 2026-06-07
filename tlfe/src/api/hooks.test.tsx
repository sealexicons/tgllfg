// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook } from "@testing-library/react";
import { AxiosError, type AxiosResponse } from "axios";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import { useLexSearch } from "./hooks";
import { shouldRetry } from "./queryClient";

function axiosErrorWithStatus(status: number): AxiosError {
  return new AxiosError("err", "ERR", undefined, undefined, {
    status,
  } as unknown as AxiosResponse);
}

describe("shouldRetry", () => {
  it("does not retry 4xx client errors", () => {
    expect(shouldRetry(0, axiosErrorWithStatus(400))).toBe(false);
    expect(shouldRetry(0, axiosErrorWithStatus(422))).toBe(false);
  });

  it("retries transient 5xx / network errors up to twice", () => {
    expect(shouldRetry(0, axiosErrorWithStatus(503))).toBe(true);
    expect(shouldRetry(1, new Error("network"))).toBe(true);
    expect(shouldRetry(2, axiosErrorWithStatus(503))).toBe(false);
  });
});

describe("useLexSearch", () => {
  it("stays idle (does not fetch) for an empty query", () => {
    const queryClient = new QueryClient();
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    const { result } = renderHook(() => useLexSearch({ q: "  " }), { wrapper });
    expect(result.current.fetchStatus).toBe("idle");
  });
});
