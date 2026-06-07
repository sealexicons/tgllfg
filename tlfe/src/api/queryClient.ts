// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { QueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";

// Don't retry 4xx (a bad request won't succeed on retry); do retry transient
// network / 5xx failures a couple of times. Exported for unit testing.
export function shouldRetry(failureCount: number, error: unknown): boolean {
  const status = error instanceof AxiosError ? error.response?.status : undefined;
  if (status !== undefined && status >= 400 && status < 500) {
    return false;
  }
  return failureCount < 2;
}

// Server-state defaults for the inspector: parses are deterministic per
// sentence, so results stay fresh briefly and don't refetch on window focus.
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      gcTime: 5 * 60_000,
      retry: shouldRetry,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});
