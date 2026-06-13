// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Radix Popover (the c-structure node popover) positions content with Popper —
// which observes the trigger via ResizeObserver — and captures pointers on its
// dismiss layer. jsdom ships none of these, so stub them for the component tests.
const globalObj = globalThis as unknown as Record<string, unknown>;
globalObj.ResizeObserver ??= class {
  observe() {}
  unobserve() {}
  disconnect() {}
};

const elementProto = Element.prototype as unknown as Record<string, unknown>;
elementProto.hasPointerCapture ??= () => false;
elementProto.setPointerCapture ??= () => {};
elementProto.releasePointerCapture ??= () => {};
elementProto.scrollIntoView ??= () => {};

afterEach(() => {
  cleanup();
});
