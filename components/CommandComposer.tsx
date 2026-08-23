'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

/**
 * The executive command input. Posts an intent to /api/missions; the server
 * queues it, decomposes it into a mission owned by the CTO, and dispatches to
 * the runtime. This UI only routes — Hermes executes.
 */
export function CommandComposer() {
  const [intent, setIntent] = useState('');
  const [priority, setPriority] = useState<'P0' | 'P1' | 'P2'>('P1');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!intent.trim() || busy) return;
    setBusy(true);
    setError(null);
    setOk(null);
    try {
      const res = await fetch('/api/missions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: 'operator', intent: intent.trim(), priority }),
      });
      const body = await res.json();
      if (!res.ok) throw new Error(body.error || 'command failed');
      setOk(`mission ${body.mission.id} created · run ${body.command.status}`);
      setIntent('');
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <input
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          placeholder="Issue an executive command, e.g. Build the NeuroGrid prototype"
          className="min-w-0 flex-1 rounded-sm-t border border-os-border bg-os-surface px-3 py-2.5 font-mono text-[12.5px] text-os-text placeholder:text-os-dim focus:border-[var(--accent-line)] focus:outline-none"
        />
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value as 'P0' | 'P1' | 'P2')}
          className="rounded-sm-t border border-os-border bg-os-surface px-2 py-2.5 font-mono text-[11px] uppercase text-os-muted focus:border-[var(--accent-line)] focus:outline-none"
          aria-label="priority"
        >
          <option value="P0">P0</option>
          <option value="P1">P1</option>
          <option value="P2">P2</option>
        </select>
        <button
          type="submit"
          disabled={busy || !intent.trim()}
          className="shrink-0 rounded-sm-t border border-[var(--accent-line)] bg-[var(--accent-soft)] px-3.5 py-2.5 font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-os-accent transition-colors hover:bg-[color-mix(in_oklab,var(--accent)_18%,transparent)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? 'Routing…' : 'Dispatch'}
        </button>
      </div>
      {error && <div className="font-mono text-[11px] text-os-err">{error}</div>}
      {ok && <div className="font-mono text-[11px] text-os-ok">{ok}</div>}
      <div className="font-mono text-[10px] text-os-dim">
        Task decomposed &amp; gated by the change policy · FounderOS routes · Hermes executes
      </div>
    </form>
  );
}
