// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { client } from "./client/client.gen";

// The generated SDK emits absolute, /api/v1-prefixed paths (the FastAPI
// mount point), so the default base is same-origin (""): `vite dev` proxies
// /api → the local `tgllfg serve`, and the nginx image reverse-proxies the
// same path to tlbe — identical in dev and prod, no CORS. Set
// VITE_API_BASE_URL to point the SDK at a different host.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// Configure the SDK's shared axios client. Called once from main.tsx before
// the app renders (and before any query runs).
export function configureApiClient(): void {
  client.setConfig({ baseURL: API_BASE_URL });
  // Auth seam (keycloak mode — out of scope for Phase 14): attach a bearer
  // token here when introduced, e.g.
  //   client.instance.interceptors.request.use((cfg) => cfg);
}
