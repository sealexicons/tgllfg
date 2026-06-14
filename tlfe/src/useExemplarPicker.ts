// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { useEffect, useMemo, useRef, useState } from "react";

import type { ExemplarSource } from "./api/client";
import { useExemplars } from "./api/hooks";

const EMPTY: ExemplarSource[] = [];

// One leaf of the corpus, with its position in the cascade. The flat list is
// the document-order walk Ctrl+↑/↓ steps through (and wraps around).
interface FlatItem {
  s: number; // source index
  sec: number; // section index within the source
  sent: number; // sentence index within the section
  text: string; // normalized text to drop into the input
}

export interface ExemplarPickerState {
  sources: ExemplarSource[];
  ready: boolean;
  isLoading: boolean;
  sourceIdx: number;
  sectionIdx: number;
  sentenceIdx: number;
  selectSource: (i: number) => void;
  selectSection: (j: number) => void;
  selectSentence: (k: number) => void;
  step: (delta: number) => void;
}

// Picker selection state over the corpus. `onPick` fires with the chosen text
// on every *user* action (dropdown change or step) — never on mount, so opening
// the picker doesn't clobber whatever is already typed. The first step only
// syncs the field to the currently-shown exemplar (shell-history style); further
// steps move and wrap across sections and sources.
export function useExemplarPicker(
  enabled: boolean,
  onPick: (text: string) => void,
): ExemplarPickerState {
  const query = useExemplars(enabled);
  const sources = query.data?.sources ?? EMPTY;

  const flat = useMemo<FlatItem[]>(() => {
    const items: FlatItem[] = [];
    sources.forEach((src, s) =>
      src.sections.forEach((section, sec) =>
        section.sentences.forEach((sentence, sent) =>
          items.push({ s, sec, sent, text: sentence.text }),
        ),
      ),
    );
    return items;
  }, [sources]);

  const [pos, setPos] = useState(0);

  const safePos = flat.length ? Math.min(pos, flat.length - 1) : 0;
  const here = flat[safePos] ?? { s: 0, sec: 0, sent: 0, text: "" };

  // Auto-sync the field to the shown exemplar once the picker is open and loaded
  // (and again whenever it's reopened), so the current selection lands in the
  // field without a first keystroke. Stepping / typing later doesn't re-trigger
  // it (the ref guards it); closing resets so reopening re-syncs. `onPick`
  // changes identity each render, so the effect re-runs each render — the guard
  // keeps it a no-op until the next open.
  const syncedRef = useRef(false);
  useEffect(() => {
    if (enabled && flat.length) {
      if (!syncedRef.current) {
        syncedRef.current = true;
        onPick(flat[Math.min(pos, flat.length - 1)].text);
      }
    } else {
      syncedRef.current = false;
    }
  }, [enabled, flat, pos, onPick]);

  function goto(nextPos: number): void {
    if (!flat.length) return;
    const wrapped = ((nextPos % flat.length) + flat.length) % flat.length;
    setPos(wrapped);
    onPick(flat[wrapped].text);
  }

  function firstPosOf(pred: (it: FlatItem) => boolean): number {
    const i = flat.findIndex(pred);
    return i >= 0 ? i : safePos;
  }

  return {
    sources,
    ready: flat.length > 0,
    isLoading: query.isLoading,
    sourceIdx: here.s,
    sectionIdx: here.sec,
    sentenceIdx: here.sent,
    selectSource: (i) => goto(firstPosOf((it) => it.s === i)),
    selectSection: (j) => goto(firstPosOf((it) => it.s === here.s && it.sec === j)),
    selectSentence: (k) =>
      goto(firstPosOf((it) => it.s === here.s && it.sec === here.sec && it.sent === k)),
    step: (delta) => goto(safePos + delta),
  };
}
