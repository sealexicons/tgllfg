// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { type ReactElement } from "react";
import { Select } from "radix-ui";

import { type ExemplarPickerState } from "./useExemplarPicker";

function PickerSelect({
  label,
  value,
  current,
  onValueChange,
  onStep,
  items,
}: {
  label: string;
  value: string;
  current: string;
  onValueChange: (value: string) => void;
  onStep: (delta: number) => void;
  items: { value: string; label: string }[];
}): ReactElement {
  return (
    <Select.Root value={value} onValueChange={onValueChange}>
      <Select.Trigger
        aria-label={label}
        onKeyDown={(event) => {
          // Ctrl/Meta + ↑/↓ steps the exemplar (and syncs the field) rather than
          // opening the dropdown; preventDefault makes Radix skip its own open.
          if (
            (event.key === "ArrowUp" || event.key === "ArrowDown") &&
            (event.ctrlKey || event.metaKey) &&
            !event.altKey
          ) {
            event.preventDefault();
            onStep(event.key === "ArrowDown" ? 1 : -1);
          }
        }}
        className="inline-flex max-w-[16rem] items-center gap-1 rounded border border-slate-300 bg-white px-2 py-1 text-slate-700 hover:border-slate-400 focus:outline-none focus:ring-1 focus:ring-violet-500"
      >
        <span className="text-slate-400">{label}:</span>
        {/* Render the label directly (not Select.Value): Radix can't resolve a
            controlled value's text until its items have been mounted (opened). */}
        <span className="truncate">{current}</span>
        <Select.Icon className="text-slate-400">▾</Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content
          position="popper"
          sideOffset={4}
          className="z-50 max-h-72 overflow-auto rounded border border-slate-200 bg-white text-xs shadow-md"
        >
          <Select.Viewport className="p-1">
            {items.map((it) => (
              <Select.Item
                key={it.value}
                value={it.value}
                className="cursor-pointer select-none rounded px-2 py-1 text-slate-700 outline-none data-[highlighted]:bg-violet-100 data-[state=checked]:font-medium"
              >
                <Select.ItemText>{it.label}</Select.ItemText>
              </Select.Item>
            ))}
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
}

// The exemplar picker: cascading source → section → sentence dropdowns. Labels
// are lowercased; an empty section (a slash-less locator) shows as "—".
export function ExemplarPicker({ picker }: { picker: ExemplarPickerState }): ReactElement {
  if (picker.isLoading) {
    return <p className="text-xs text-slate-400">Loading exemplars…</p>;
  }
  if (!picker.ready) {
    return <p className="text-xs text-slate-400">No exemplars available.</p>;
  }
  const source = picker.sources[picker.sourceIdx];
  const section = source.sections[picker.sectionIdx];
  return (
    <div className="flex flex-wrap items-center gap-2 text-xs">
      <PickerSelect
        label="source"
        value={String(picker.sourceIdx)}
        current={source.source.toLowerCase()}
        onValueChange={(v) => picker.selectSource(Number(v))}
        onStep={picker.step}
        items={picker.sources.map((s, i) => ({ value: String(i), label: s.source.toLowerCase() }))}
      />
      <PickerSelect
        label="section"
        value={String(picker.sectionIdx)}
        current={section.section.toLowerCase() || "—"}
        onValueChange={(v) => picker.selectSection(Number(v))}
        onStep={picker.step}
        items={source.sections.map((s, j) => ({
          value: String(j),
          label: s.section.toLowerCase() || "—",
        }))}
      />
      <PickerSelect
        label="sentence"
        value={String(picker.sentenceIdx)}
        current={section.sentences[picker.sentenceIdx].sentence.toLowerCase()}
        onValueChange={(v) => picker.selectSentence(Number(v))}
        onStep={picker.step}
        items={section.sentences.map((s, k) => ({
          value: String(k),
          label: s.sentence.toLowerCase(),
        }))}
      />
      <span className="text-slate-400">Ctrl+↑/↓ to step</span>
    </div>
  );
}
