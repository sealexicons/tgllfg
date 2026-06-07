// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Override the API base URL (default: same-origin — /api/v1 is proxied to tlbe). */
  readonly VITE_API_BASE_URL?: string;
}
