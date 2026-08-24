import { getDb } from '@/lib/data';
import { controlPlaneSummary } from '@/lib/control-plane';
import { pendingApprovals } from '@/lib/governance';
import { PageHeader } from '@/components/PageHeader';
import { Badge, Dot, Kbd, Label, SectionHead } from '@/components/terminal';
import { GateLadder } from '@/components/GateLadder';
import { CommandComposer } from '@/components/CommandComposer';
import type { MissionStatus } from '@/lib/schemas';

export const dynamic = 'force-dynamic';

const STATUS_TONE: Record<MissionStatus, 'ok' | 'warn' | 'err' | 'default' | 'accent'> = {
  executing: 'ok',
  awaiting_approval: 'warn',
  blocked: 'err',
  complete: 'ok',
  proposed: 'default',
  failed: 'err',
};

const STATUS_DOT: Record<MissionStatus, string> = {
  executing: 'ok',
  awaiting_approval: 'warn',
  blocked: 'err',
  complete: 'ok',
  proposed: 'off',
  failed: 'err',
};

function priorityTone(p: string): 'accent' | 'warn' | 'default' {
  if (p === 'P0') return 'accent';
  if (p === 'P1') return 'warn';
  return 'default';
}

export default async function MissionControlPage() {
  const db = getDb();
  const summary = controlPlaneSummary(db);
  const missions = db.missions.all();
  const commands = db.commands.all().slice(0, 6);
  const openApprovals = pendingApprovals(db);
  const audit = db.events.recent(12);

  return (
    <div>
      <PageHeader
        eyebrow="nura command center"
        title="Mission Control"
        caret
        right={<Kbd>⌘K</Kbd>}
      />

      {/* Executive state line */}
      <div className="-mt-3 mb-[18px] flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[12px]">
        <span className="text-os-muted">
          {summary.total} missions · {summary.executing} executing ·{' '}
          {summary.awaitingApproval} awaiting approval · {summary.blocked} blocked
        </span>
      </div>

      {/* Summary pulse row */}
      <section className="mb-[18px] grid grid-cols-4 gap-3 max-[1100px]:grid-cols-2">
        {[
          { label: 'Executing', value: summary.executing, tone: 'text-os-ok', href: '/mission-control' },
          { label: 'Awaiting approval', value: summary.awaitingApproval, tone: 'text-os-warn', href: '/mission-control' },
          { label: 'Blocked', value: summary.blocked, tone: 'text-os-err', href: '/mission-control' },
          { label: 'Complete', value: summary.complete, tone: 'text-os-accent', href: '/mission-control' },
        ].map((s) => (
          <div key={s.label} className="flex flex-col gap-2 rounded-lg-t border border-os-border bg-os-surface px-[18px] py-4">
            <Label>{s.label}</Label>
            <div className={`font-mono text-[26px] font-semibold tracking-[-0.02em] ${s.tone}`}>{s.value}</div>
          </div>
        ))}
      </section>

      {/* Governance — approval inbox (human-in-the-loop) */}
      <section className="mb-[22px]">
        <SectionHead label="Approval inbox" count={`${openApprovals.length} awaiting decision`} />
        {openApprovals.length === 0 ? (
          <div className="rounded-lg-t border border-os-border bg-os-bg2 px-4 py-3 font-mono text-[11px] text-os-muted">
            No open approvals — every armed gate has been decided.
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {openApprovals.map((a) => (
              <div key={a.id} className="flex items-center justify-between gap-4 rounded-lg-t border border-os-border bg-os-surface px-[18px] py-3">
                <div className="min-w-0 font-mono text-[11px]">
                  <div className="flex items-center gap-2">
                    <Dot state="warn" pulse />
                    <span className="uppercase tracking-[0.08em]">{a.gate}</span>
                    <span className="text-os-dim">· requested by {a.requestedBy}</span>
                  </div>
                  <div className="mt-1 truncate text-os-muted">{db.missions.byId(a.missionId)?.mission ?? a.missionId}</div>
                </div>
                <span className="shrink-0 font-mono text-[10px] text-os-dim">{a.id.slice(0, 12)}</span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Command composer — the executive input surface */}
      <section className="mb-[22px]">
        <SectionHead label="Command bus" count="issue an executive command" />
        <CommandComposer />
      </section>

      {/* Missions */}
      <section className="mb-[22px]">
        <SectionHead label="Missions" count={`${missions.length} active`} />
        <div className="flex flex-col gap-3">
          {missions.map((m) => (
            <div key={m.id} className="rounded-lg-t border border-os-border bg-os-surface px-[18px] py-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2.5">
                    <Badge tone={priorityTone(m.priority)}>{m.priority}</Badge>
                    <span className="text-[14.5px] font-semibold">{m.mission}</span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-2 font-mono text-[10.5px] text-os-dim">
                    <Dot state={STATUS_DOT[m.status]} pulse={m.status === 'executing'} />
                    <span className="uppercase tracking-[0.08em]">{m.status}</span>
                    <span>·</span>
                    <span>owner: {m.ownerAgentId}</span>
                    {m.artifacts.length > 0 && (
                      <>
                        <span>·</span>
                        <span>{m.artifacts.length} artifacts</span>
                      </>
                    )}
                    {m.evidence.length > 0 && (
                      <>
                        <span>·</span>
                        <span className="text-os-ok">{m.evidence.length} evidence</span>
                      </>
                    )}
                  </div>
                </div>
                <span className="shrink-0 font-mono text-[10px] text-os-dim">{m.id}</span>
              </div>

              <div className="mt-3">
                <GateLadder mission={m} />
              </div>

              {m.tasks.length > 0 && (
                <div className="mt-3 border-t border-os-border pt-3">
                  <Label count={m.tasks.length}>tasks</Label>
                  <div className="mt-2 grid grid-cols-1 gap-1 sm:grid-cols-2">
                    {m.tasks.map((t) => (
                      <div key={t.id} className="flex items-center gap-2 rounded-sm-t border border-os-border bg-os-bg2 px-2.5 py-1.5 font-mono text-[11px]">
                        <span className={`dot ${t.status === 'done' ? 'ok' : t.status === 'in_progress' ? 'warn' : 'off'}`} />
                        <span className="min-w-0 flex-1 truncate text-os-muted">{t.title}</span>
                        <span className="shrink-0 text-os-dim">{t.ownerAgentId}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Recent commands */}
      {commands.length > 0 && (
        <section>
          <SectionHead label="Recent commands" count={commands.length} />
          <ul className="flex flex-col gap-1.5">
            {commands.map((c) => (
              <li
                key={c.id}
                className="flex items-baseline gap-2.5 rounded-sm-t border border-os-border bg-os-surface px-3 py-2 font-mono text-[11px]"
              >
                <span className="shrink-0 text-os-accent">{c.source}</span>
                <span className="min-w-0 flex-1 truncate text-os-muted">{c.intent}</span>
                <span className="shrink-0 text-os-dim">{c.status}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Governance — immutable audit trail */}
      {audit.length > 0 && (
        <section className="mt-[22px]">
          <SectionHead label="Audit trail" count={`${audit.length} recent events`} />
          <ul className="flex flex-col gap-1.5">
            {audit.map((e) => (
              <li
                key={e.id}
                className="flex items-baseline gap-2.5 rounded-sm-t border border-os-border bg-os-surface px-3 py-2 font-mono text-[11px]"
              >
                <span className="shrink-0 text-os-dim">{e.at.slice(11, 19)}</span>
                <span className="shrink-0 text-os-accent">{e.actor}</span>
                <span className="shrink-0 uppercase tracking-[0.06em]">{e.action}</span>
                <span className="min-w-0 flex-1 truncate text-os-muted">{e.detail || e.missionId}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
