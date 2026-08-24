import { randomUUID } from 'node:crypto';
import type { FounderDb } from '@/lib/db';
import {
  ApprovalSchema,
  MissionEventSchema,
  type Approval,
  type ApprovalStatus,
  type GateId,
  type GateStatus,
  type Mission,
  type MissionEvent,
  type MissionEventAction,
} from '@/lib/schemas';

/**
 * NURA Governance.
 *
 * The control plane (lib/control-plane.ts) owns POLICY — the gate ladder and
 * mission lifecycle. This module owns EVIDENCE — the immutable, replayable audit
 * trail and the governed approval inbox. A control plane that changes state
 * without recording who did it, under which gate, with what justification, is
 * not governance — it's a demo.
 *
 * Invariants enforced here:
 *   1. Every consequential write emits an immutable MissionEvent.
 *   2. A gate may only be marked `pass` when the mission carries evidence that
 *      backs it. "No evidence = no pass."
 *   3. An approval is a governed decision: it captures the approver identity,
 *      a rationale, and a timestamp, and it is itself audited.
 */

const now = () => new Date().toISOString();

/** Append one immutable governance event. This is the audit trail's write path. */
export function logEvent(
  db: FounderDb,
  input: { missionId: string; actor: string; action: MissionEventAction; gate?: GateId | null; detail?: string },
): MissionEvent {
  // Actor identity is mandatory — an anonymous write is not auditable.
  if (!input.actor?.trim()) {
    throw new Error('governance: actor is required to log an event');
  }
  const event = MissionEventSchema.parse({
    id: randomUUID(),
    missionId: input.missionId,
    actor: input.actor.trim(),
    action: input.action,
    gate: input.gate ?? null,
    detail: input.detail ?? '',
    at: now(),
  });
  db.events.insert(event);
  return event;
}

/** Reject a gate pass that carries no evidence. Returns null + detail, else the event. */
export function requireEvidenceToPass(
  db: FounderDb,
  mission: Mission,
  gate: GateId,
  actor: string,
): { ok: true } | { ok: false; detail: string } {
  if (mission.evidence.length === 0) {
    const detail = `gate '${gate}' cannot pass: mission has no evidence to back it`;
    logEvent(db, { missionId: mission.id, actor, action: 'gate_pass_denied_no_evidence', gate, detail });
    return { ok: false, detail };
  }
  return { ok: true };
}

/**
 * Attach evidence to a mission AND emit the auditable event. Evidence is a
 * concrete handle (build id, test run, review handle, commit SHA) — never an
 * empty string or a claim.
 */
export function attachEvidence(db: FounderDb, missionId: string, evidence: string, actor: string): Mission {
  const trimmed = evidence.trim();
  if (!trimmed) {
    throw new Error('governance: evidence must be a concrete, non-empty handle');
  }
  const mission = db.missions.byId(missionId);
  if (!mission) throw new Error(`governance: unknown mission ${missionId}`);
  db.missions.addEvidence(missionId, trimmed, now());
  logEvent(db, { missionId, actor, action: 'evidence_attached', detail: trimmed });
  return db.missions.byId(missionId)!;
}

/**
 * Advance a gate under governance. Applies the evidence-before-pass rule and
 * writes the audit event for every transition (including denials).
 */
export function advanceGateGoverned(
  db: FounderDb,
  missionId: string,
  gate: GateId,
  status: GateStatus,
  actor: string,
): { mission: Mission | null; denial?: string } {
  const mission = db.missions.byId(missionId);
  if (!mission) return { mission: null };

  // Enforce evidence-before-pass at the domain layer (not just in the route).
  if (status === 'pass' && !mission.evidence.some((e) => e.trim())) {
    const denied = requireEvidenceToPass(db, mission, gate, actor);
    return { mission: db.missions.byId(missionId), denial: denied.ok ? undefined : denied.detail };
  }

  const prior = mission.gates[gate];
  const next = db.controlPlaneSetGate(missionId, gate, status);
  if (!next) return { mission: null };

  logEvent(db, {
    missionId,
    actor,
    action: status === 'waiting' ? 'gate_waiting' : 'gate_change',
    gate,
    detail: `${gate}: ${prior ?? 'pending'} → ${status}`,
  });

  if (status === 'waiting') {
    // A waiting gate arms approval — record the governed approval request.
    requestApproval(db, missionId, gate, actor);
  } else if (status === 'pass' && db.missions.all() && everyGatePass(db, missionId)) {
    db.missions.setStatus(missionId, 'complete', now());
    logEvent(db, { missionId, actor, action: 'mission_complete', detail: 'all gates pass' });
  }

  return { mission: db.missions.byId(missionId) };
}

function everyGatePass(db: FounderDb, missionId: string): boolean {
  const m = db.missions.byId(missionId);
  if (!m) return false;
  return Object.values(m.gates).every((g) => g === 'pass');
}

/** Create an approval request for a mission gate. Open until decided. */
export function requestApproval(db: FounderDb, missionId: string, gate: GateId, actor: string): Approval {
  const existing = db.approvals.openForGate(missionId, gate);
  if (existing) return existing; // idempotent — don't double-queue an open request
  const approval = ApprovalSchema.parse({
    id: randomUUID(),
    missionId,
    gate,
    requestedBy: actor,
    requestedAt: now(),
    status: 'open',
    decidedBy: null,
    rationale: '',
    decidedAt: null,
  });
  db.approvals.insert(approval);
  db.events.insert(
    MissionEventSchema.parse({
      id: randomUUID(),
      missionId,
      actor,
      action: 'approval_requested',
      gate,
      detail: `approval for gate '${gate}'`,
      at: now(),
    }),
  );
  return approval;
}

/**
 * Decide an open approval. Records the approver identity + rationale, emits the
 * auditable decision, and applies the consequence to the mission gate:
 *   approved -> gate pass (if evidence backs it; else denied) -> mission resumes
 *   rejected -> gate fail -> mission blocked
 */
export function decideApproval(
  db: FounderDb,
  approvalId: string,
  decision: 'approved' | 'rejected',
  actor: string,
  rationale = '',
): { approval: Approval | null; mission: Mission | null; error?: string } {
  const approval = db.approvals.byId(approvalId);
  if (!approval) return { approval: null, mission: null, error: 'unknown approval' };
  if (approval.status !== 'open') {
    return { approval, mission: db.missions.byId(approval.missionId), error: 'approval already decided' };
  }

  const decidedAt = now();
  db.approvals.decide(approvalId, decision as ApprovalStatus, actor, rationale.trim(), decidedAt);
  db.events.insert(
    MissionEventSchema.parse({
      id: randomUUID(),
      missionId: approval.missionId,
      actor,
      action: 'approval_decided',
      gate: approval.gate,
      detail: `approval '${decision}' by ${actor}${rationale ? ` — ${rationale.trim()}` : ''}`,
      at: decidedAt,
    }),
  );

  // Apply the consequence through the governed gate path.
  if (decision === 'approved') {
    const res = advanceGateGoverned(db, approval.missionId, approval.gate, 'pass', actor);
    return { approval: db.approvals.byId(approvalId), mission: res.mission, error: res.denial };
  }
  const set = db.controlPlaneSetGate(approval.missionId, approval.gate, 'fail');
  return { approval: db.approvals.byId(approvalId), mission: set ? db.missions.byId(approval.missionId) : null };
}

/** The governed approval inbox — open approvals needing a human decision. */
export function pendingApprovals(db: FounderDb): Approval[] {
  return db.approvals.open();
}

/** Full replayable audit trail for a mission, newest first. */
export function missionAudit(db: FounderDb, missionId: string): MissionEvent[] {
  return db.events.forMission(missionId);
}
