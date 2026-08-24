import { afterEach, describe, expect, test } from 'vitest';
import { openDb, type FounderDb } from '@/lib/db';
import { decomposeCommand, queueCommand } from '@/lib/control-plane';
import {
  advanceGateGoverned,
  attachEvidence,
  decideApproval,
  logEvent,
  missionAudit,
  pendingApprovals,
  requestApproval,
  requireEvidenceToPass,
} from '@/lib/governance';

let db: FounderDb;

afterEach(() => {
  db?.close();
});

const seedMission = (opts: { priority?: 'P0' | 'P1' | 'P2' | 'P3' } = {}) => {
  const command = queueCommand(db, 'ceo', 'Build the first NeuroGrid prototype');
  const mission = decomposeCommand(db, { source: command.source, intent: command.intent }, { priority: opts.priority ?? 'P0' });
  return { command, mission };
};

describe('Governance — immutable audit trail', () => {
  test('state transitions emit audit events with actor + timestamp', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    const event = logEvent(db, { missionId: mission.id, actor: 'hermes-cto', action: 'status_changed', detail: 'proposed → executing' });
    expect(event.actor).toBe('hermes-cto');
    expect(event.action).toBe('status_changed');
    expect(event.at).toBeTruthy();
    expect(missionAudit(db, mission.id).length).toBeGreaterThanOrEqual(1);
  });

  test('an anonymous actor is rejected — an unowned write is not auditable', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    expect(() => logEvent(db, { missionId: mission.id, actor: '  ', action: 'status_changed' })).toThrow();
  });

  test('events are replayable and ordered newest-first', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    for (let i = 0; i < 3; i++) attachEvidence(db, mission.id, `handle-${i}`, 'operator');
    const audit = missionAudit(db, mission.id);
    expect(audit.length).toBe(3);
    expect(audit[0].action).toBe('evidence_attached');
  });
});

describe('Governance — evidence-before-pass', () => {
  test('a gate cannot pass with zero evidence, and the denial is audited', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    const res = advanceGateGoverned(db, mission.id, 'build', 'pass', 'hermes-cto');
    expect(res.denial).toMatch(/no evidence/);
    expect(db.missions.byId(mission.id)?.gates.build).not.toBe('pass');
    // The denial itself was audited.
    expect(missionAudit(db, mission.id).some((e) => e.action === 'gate_pass_denied_no_evidence')).toBe(true);
  });

  test('after evidence is attached, the gate can pass', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    attachEvidence(db, mission.id, 'build-abc123', 'operator');
    const res = advanceGateGoverned(db, mission.id, 'build', 'pass', 'hermes-cto');
    expect(res.denial).toBeUndefined();
    expect(db.missions.byId(mission.id)?.gates.build).toBe('pass');
  });

  test('requireEvidenceToPass reports ok when evidence exists', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    const denied = requireEvidenceToPass(db, mission, 'security', 'operator');
    expect(denied.ok).toBe(false);
    attachEvidence(db, mission.id, 'sec-review-1', 'operator');
    const ok = requireEvidenceToPass(db, db.missions.byId(mission.id)!, 'security', 'operator');
    expect(ok.ok).toBe(true);
  });
});

describe('Governance — approval inbox lifecycle', () => {
  test('a waiting gate arms a governed approval request (idempotent)', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    attachEvidence(db, mission.id, 'clinical-1', 'operator');
    const res = advanceGateGoverned(db, mission.id, 'clinical', 'waiting', 'clinical-intelligence');
    expect(res.denial).toBeUndefined();
    const open = pendingApprovals(db);
    expect(open.length).toBe(1);
    expect(open[0].gate).toBe('clinical');
    // Requesting again must not double-queue.
    requestApproval(db, mission.id, 'clinical', 'clinical-intelligence');
    expect(pendingApprovals(db).length).toBe(1);
  });

  test('approve applies a pass and resumes; reject blocks', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    attachEvidence(db, mission.id, 'clinical-2', 'operator');
    advanceGateGoverned(db, mission.id, 'clinical', 'waiting', 'clinical-intelligence');
    const approval = pendingApprovals(db)[0];

    const decided = decideApproval(db, approval.id, 'approved', 'eddie', 'clinical gate looks sound');
    expect(decided.error).toBeUndefined();
    const a = db.approvals.byId(approval.id)!;
    expect(a.status).toBe('approved');
    expect(a.decidedBy).toBe('eddie');
    expect(a.rationale).toBe('clinical gate looks sound');
    // Approving passes the gate.
    expect(db.missions.byId(mission.id)?.gates.clinical).toBe('pass');
    // The decision was audited.
    expect(missionAudit(db, mission.id).some((e) => e.action === 'approval_decided')).toBe(true);
  });

  test('rejecting fails the gate and blocks the mission', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    attachEvidence(db, mission.id, 'sec-1', 'operator');
    advanceGateGoverned(db, mission.id, 'security', 'waiting', 'cybersecurity');
    const approval = pendingApprovals(db)[0];
    decideApproval(db, approval.id, 'rejected', 'eddie', 'failed the review');
    expect(db.missions.byId(mission.id)?.gates.security).toBe('fail');
    expect(db.missions.byId(mission.id)?.status).toBe('blocked');
  });

  test('an already-decided approval cannot be decided twice', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    attachEvidence(db, mission.id, 'sec-2', 'operator');
    advanceGateGoverned(db, mission.id, 'security', 'waiting', 'cybersecurity');
    const approval = pendingApprovals(db)[0];
    decideApproval(db, approval.id, 'approved', 'eddie');
    const again = decideApproval(db, approval.id, 'rejected', 'eddie');
    expect(again.error).toMatch(/already decided/);
  });

  test('an approve without evidence reports the denial rather than silently passing', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    advanceGateGoverned(db, mission.id, 'security', 'waiting', 'cybersecurity');
    const approval = pendingApprovals(db)[0];
    const decided = decideApproval(db, approval.id, 'approved', 'eddie');
    expect(decided.error).toMatch(/no evidence/);
    expect(db.missions.byId(mission.id)?.gates.security).not.toBe('pass');
  });
});

describe('Governance — evidence attachment', () => {
  test('evidence must be a concrete handle, not an empty claim', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    expect(() => attachEvidence(db, mission.id, '   ', 'operator')).toThrow();
  });
});
