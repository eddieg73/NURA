import { GATE_LABELS, GATE_RANK } from '@/lib/control-plane';
import type { GateId, GateStatus, Mission } from '@/lib/schemas';

/** Color + label per gate status, matching the honest status palette. */
const GATE_TONE: Record<GateStatus, { text: string; dot: string }> = {
  pass: { text: 'ok', dot: 'ok' },
  pending: { text: 'dim', dot: 'off' },
  review: { text: 'warn', dot: 'warn' },
  waiting: { text: 'warn', dot: 'warn' },
  fail: { text: 'err', dot: 'err' },
};

const GATE_TEXT: Record<GateStatus, { cls: string; badgeTone: string }> = {
  pass: { cls: 'text-os-ok', badgeTone: 'ok' },
  pending: { cls: 'text-os-dim', badgeTone: 'default' },
  review: { cls: 'text-os-warn', badgeTone: 'warn' },
  waiting: { cls: 'text-os-warn', badgeTone: 'warn' },
  fail: { cls: 'text-os-err', badgeTone: 'err' },
};

/** One gate chip in the change-policy ladder. Shows label + live status. */
export function GateChip({ mission, gate }: { mission: Mission; gate: GateId }) {
  const status = mission.gates[gate] ?? 'pending';
  const tone = GATE_TEXT[status];
  const dot = GATE_TONE[status].dot;
  return (
    <div className="flex items-center gap-1.5 rounded-sm-t border border-os-border bg-os-surface px-2 py-1.5 font-mono text-[9.5px] uppercase tracking-[0.12em]">
      <span className={`dot ${dot}`} />
      <span className="text-os-dim">{GATE_LABELS[gate]}</span>
      <span className={tone.cls}>{status}</span>
    </div>
  );
}

export function GateLadder({ mission }: { mission: Mission }) {
  const order = Object.keys(GATE_LABELS) as GateId[];
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {order.map((gate, i) => (
        <span key={gate} className="flex items-center gap-1.5">
          <GateChip mission={mission} gate={gate} />
          {i < order.length - 1 && <span className="text-os-border-strong">→</span>}
        </span>
      ))}
    </div>
  );
}
