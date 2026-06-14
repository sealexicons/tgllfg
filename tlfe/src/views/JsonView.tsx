// Copyright (c) 2025-2026 G & R Associates LLC
// SPDX-License-Identifier: MIT OR Apache-2.0

import { useEffect, useRef, useState, type MouseEvent, type ReactElement } from "react";
import { createPortal } from "react-dom";
import { Tooltip } from "radix-ui";

import type { ParseResponse } from "../api/client";

const pad2 = (n: number) => String(n).padStart(2, "0");
const pad3 = (n: number) => String(n).padStart(3, "0");

// tgllfg-parse-YYMMDDhhmmssuuu.json — local time, millisecond precision so two
// downloads in the same session never collide.
function downloadName(now: Date): string {
  const stamp =
    pad2(now.getFullYear() % 100) +
    pad2(now.getMonth() + 1) +
    pad2(now.getDate()) +
    pad2(now.getHours()) +
    pad2(now.getMinutes()) +
    pad2(now.getSeconds()) +
    pad3(now.getMilliseconds());
  return `tgllfg-parse-${stamp}.json`;
}

// The File System Access API (Chromium) isn't in the standard DOM lib types;
// declare the slice we use so the picker stays type-checked, not `any`.
interface SaveFilePickerOptions {
  suggestedName?: string;
  types?: { description?: string; accept: Record<string, string[]> }[];
}
interface WritableFileStream {
  write(data: Blob): Promise<void>;
  close(): Promise<void>;
}
interface SaveFileHandle {
  createWritable(): Promise<WritableFileStream>;
}
type SaveFilePicker = (options?: SaveFilePickerOptions) => Promise<SaveFileHandle>;

// Object URLs minted by fallback downloads, revoked together on page unload.
// A legacy <a download> has no "finished" event, and the Save dialog can stay
// open arbitrarily long (slowly navigating folders, or stepping away for a phone
// call) — so any fixed revoke timer risks firing before the browser reads the
// blob and truncating the file. `pagehide` is the one moment revocation is
// guaranteed safe; the browser reclaims these on unload regardless, so the
// per-session cost is just a handful of small JSON blobs.
const pendingDownloadUrls = new Set<string>();
let revokeSweepArmed = false;

// Direct browser download (Firefox / Safari, or if the native dialog fails).
// This goes through the browser's normal download pipeline, so it honors the
// "ask where to save each file" preference: with it on, the browser shows its
// own Save As dialog pre-filled with `filename`; with it off, it saves straight
// to the downloads folder. The `download` attribute only supplies the name.
function anchorDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  pendingDownloadUrls.add(url);
  if (!revokeSweepArmed) {
    revokeSweepArmed = true;
    window.addEventListener("pagehide", () => {
      for (const pending of pendingDownloadUrls) URL.revokeObjectURL(pending);
      pendingDownloadUrls.clear();
    });
  }
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
}

function CopyIcon(): ReactElement {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-3.5 w-3.5"
      aria-hidden="true"
    >
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function DownloadIcon(): ReactElement {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-3.5 w-3.5"
      aria-hidden="true"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

// Icon-only control: a Radix tooltip provides the hover label and `aria-label`
// the matching accessible name. We avoid the native `title` tooltip (it popped
// awkwardly by the cursor when focus returned from the Save dialog); Radix won't
// reopen after a click until the pointer leaves, so it stays out of the way.
function PaneButton({
  label,
  onClick,
  children,
}: {
  label: string;
  onClick: (event: MouseEvent<HTMLButtonElement>) => Promise<void>;
  children: ReactElement;
}): ReactElement {
  // After a mouse click, blur the button once the action settles: its focus
  // ring shouldn't linger, and (for Download) the Save dialog returns focus here
  // on close, which would otherwise re-open the focus-triggered tooltip beside
  // the snackbar. Keyboard activation (detail 0) keeps focus where it expects.
  function handleClick(event: MouseEvent<HTMLButtonElement>) {
    const button = event.currentTarget;
    const viaPointer = event.detail > 0;
    void onClick(event).finally(() => {
      if (viaPointer) button.blur();
    });
  }
  return (
    <Tooltip.Root>
      <Tooltip.Trigger asChild>
        <button
          type="button"
          onClick={handleClick}
          aria-label={label}
          className="rounded bg-slate-800/80 p-1.5 text-slate-300 backdrop-blur transition hover:bg-slate-700 hover:text-white focus:outline-none focus:ring-1 focus:ring-slate-400"
        >
          {children}
        </button>
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Content
          side="bottom"
          sideOffset={6}
          className="z-50 select-none rounded bg-slate-800 px-2 py-1 text-xs font-medium text-white shadow-md"
        >
          {label}
          <Tooltip.Arrow className="fill-slate-800" />
        </Tooltip.Content>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}

// A transient bottom-center snackbar, portaled to <body> so no ancestor's
// stacking/overflow can clip it; fades in on mount and is announced politely.
function Snackbar({ message }: { message: string }): ReactElement {
  const [shown, setShown] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setShown(true));
    return () => cancelAnimationFrame(id);
  }, []);
  return createPortal(
    <div
      role="status"
      className={`pointer-events-none fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white shadow-lg transition-opacity duration-200 ${
        shown ? "opacity-100" : "opacity-0"
      }`}
    >
      {message}
    </div>,
    document.body,
  );
}

function CopyButton({ text, notify }: { text: string; notify: (message: string) => void }) {
  async function onCopy() {
    try {
      await navigator.clipboard?.writeText(text);
      notify("Copied JSON");
    } catch {
      // Clipboard unavailable (e.g. an insecure context) — nothing to do.
    }
  }
  return (
    <PaneButton label="Copy JSON" onClick={() => onCopy()}>
      <CopyIcon />
    </PaneButton>
  );
}

function DownloadButton({ text, notify }: { text: string; notify: (message: string) => void }) {
  async function onDownload() {
    const filename = downloadName(new Date());
    const blob = new Blob([text], { type: "application/json" });
    const win = window as Window & { showSaveFilePicker?: SaveFilePicker };
    // Prefer the native Save As dialog (Chromium): it defaults to the user's
    // downloads folder + our suggested name but lets them change either.
    if (win.showSaveFilePicker) {
      try {
        const handle = await win.showSaveFilePicker({
          suggestedName: filename,
          types: [{ description: "JSON", accept: { "application/json": [".json"] } }],
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        notify("Saved JSON");
      } catch (err) {
        // Dialog dismissed → do nothing; any other failure → fall back.
        if (!(err instanceof DOMException && err.name === "AbortError")) {
          anchorDownload(blob, filename);
          notify("Saved JSON");
        }
      }
      return;
    }
    // No File System Access API (Firefox / Safari) → straight to downloads.
    anchorDownload(blob, filename);
    notify("Saved JSON");
  }
  return (
    <PaneButton label="Save JSON" onClick={() => onDownload()}>
      <DownloadIcon />
    </PaneButton>
  );
}

// The JSON tab body: the full ParseResponse, pretty-printed. Copy / Download
// controls float at the pane's top-right — left of the scrollbar and fixed as
// the payload scrolls (they sit on the non-scrolling wrapper, not in the
// <pre>); the right padding keeps the JSON from sliding under them. Both report
// success through one shared snackbar.
export function JsonView({ result }: { result: ParseResponse | undefined }): ReactElement {
  const [toast, setToast] = useState<{ message: string; nonce: number } | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);

  // Bump the nonce each call so the snackbar remounts and replays its fade-in,
  // even for back-to-back actions with the same message.
  function notify(message: string) {
    setToast((prev) => ({ message, nonce: (prev?.nonce ?? 0) + 1 }));
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setToast(null), 2000);
  }

  if (!result) {
    return <p className="text-slate-400">Parse a sentence to see the raw payload.</p>;
  }
  const json = JSON.stringify(result, null, 2);
  return (
    <div className="relative">
      <Tooltip.Provider delayDuration={300}>
        <div className="absolute right-3 top-3 z-10 flex gap-1">
          <CopyButton text={json} notify={notify} />
          <DownloadButton text={json} notify={notify} />
        </div>
      </Tooltip.Provider>
      <pre className="max-h-[28rem] overflow-auto rounded bg-slate-900 p-3 pr-20 text-xs leading-relaxed text-slate-100">
        {json}
      </pre>
      {toast && <Snackbar key={toast.nonce} message={toast.message} />}
    </div>
  );
}
