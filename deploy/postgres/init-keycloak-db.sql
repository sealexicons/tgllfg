-- Copyright (c) 2025-2026 G & R Associates LLC
-- SPDX-License-Identifier: MIT OR Apache-2.0

-- Create the Keycloak database in the shared Postgres instance (Phase 13.H,
-- `auth` profile). Runs once, on first Postgres init (empty data volume);
-- harmless when the auth profile is not used (the DB just sits empty).
CREATE DATABASE keycloak;
