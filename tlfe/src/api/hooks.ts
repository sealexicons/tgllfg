// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { keepPreviousData, useMutation, useQuery } from "@tanstack/react-query";

import {
  auditDiffApiV1AuditDiffPostMutation,
  auditRunApiV1AuditRunPostMutation,
  auditRunStatusApiV1AuditRunsRunIdGetOptions,
  lexSearchApiV1LexSearchGetOptions,
  parseEndpointApiV1ParsePostMutation,
} from "./client/@tanstack/react-query.gen";

// Thin domain hooks over the generated react-query helpers, so app code
// never touches the verbose operationId-derived names.

/**
 * Parse a Tagalog sentence. A pure compute call (no cached resource), so it
 * is modelled as a mutation: `parse.mutate({ body: { text, n_best, strict } })`.
 */
export function useParse() {
  return useMutation(parseEndpointApiV1ParsePostMutation());
}

export interface LexSearchParams {
  /** Fuzzy query against lemma citation forms. */
  q: string;
  /** Max matches to return (the endpoint is limit-only — no offset yet). */
  limit?: number;
}

/**
 * Fuzzy lemma search — a cached, deduplicated query. `keepPreviousData`
 * holds the prior results on screen while a new query/limit loads (smooth
 * incremental paging); disabled for an empty query.
 */
export function useLexSearch(params: LexSearchParams) {
  return useQuery({
    ...lexSearchApiV1LexSearchGetOptions({ query: params }),
    enabled: params.q.trim().length > 0,
    placeholderData: keepPreviousData,
  });
}

/** Start a corpus audit (background job). Returns a run id to poll. */
export function useRunAudit() {
  return useMutation(auditRunApiV1AuditRunPostMutation());
}

const AUDIT_TERMINAL: ReadonlySet<string> = new Set(["completed", "failed", "cancelled"]);

/**
 * Poll an audit run's status until it reaches a terminal state
 * (completed / failed / cancelled), refetching every 1.5s while running.
 */
export function useAuditRunStatus(runId: string | undefined) {
  return useQuery({
    ...auditRunStatusApiV1AuditRunsRunIdGetOptions({ path: { run_id: runId ?? "" } }),
    enabled: Boolean(runId),
    refetchInterval: (query) =>
      query.state.data && AUDIT_TERMINAL.has(query.state.data.status) ? false : 1500,
  });
}

/** Diff the latest audit results against the baseline. */
export function useAuditDiff() {
  return useMutation(auditDiffApiV1AuditDiffPostMutation());
}
