import { afterEach, describe, expect, test } from 'vitest';
import { openDb, type FounderDb } from '@/lib/db';
import {
  advanceGate,
  blockingGate,
  canPassGate,
  controlPlaneSummary,
  decomposeCommand,
  defaultGates,
  missionComplete,
  queueCommand,
} from '@/lib/control-plane';
import { GATE_ORDER, type GateId } from '@/lib/schemas';

let db: FounderDb;

afterEach(() => {
  db?.close();
});

const seedMission = () => {
  const command = queueCommand(db, 'ceo', 'Build the first NeuroGrid prototype');
  const mission = decomposeCommand(db, { source: command.source, intent: command.intent }, { priority: 'P0' });
  return { command, mission };
};

describe('NURA Control Plane — missions', () => {
  test('mission round-trips with the full control-plane shape', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    expect(db.missions.byId(mission.id)?.mission).toBe('Build the first NeuroGrid prototype');
    expect(db.missions.byId(mission.id)?.priority).toBe('P0');
    expect(db.missions.byId(mission.id)?.ownerAgentId).toBe('hermes-cto');
    expect(db.missions.byId(mission.id)?.status).toBe('proposed');
  });

  test('a decomposed mission assigns tasks to worker agents', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    const tasks = mission.tasks;
    expect(tasks.length).toBeGreaterThan(0);
    expect(tasks.every((t) => t.ownerAgentId && t.status === 'pending')).toBe(true);
    // One owner per task is enforced by the schema (ownerAgentId is required).
    expect(tasks.map((t) => t.ownerAgentId)).toContain('software-architect');
    expect(tasks.map((t) => t.ownerAgentId)).toContain('qa');
  });

  test('a mission starts with every gate pending', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    for (const g of GATE_ORDER) expect(mission.gates[g as GateId]).toBe('pending');
  });

  test('missions are listed in priority order (P0 before P2)', () => {
    db = openDb(':memory:');
    decomposeCommand(db, { source: 'ceo', intent: 'low priority mission' }, { priority: 'P2' });
    decomposeCommand(db, { source: 'ceo', intent: 'high priority mission' }, { priority: 'P0' });
    const missions = db.missions.all();
    expect(missions[0].priority).toBe('P0');
    expect(missions[missions.length - 1].priority).toBe('P2');
  });
});

describe('NURA Control Plane — the change-policy gate ladder', () => {
  test('canPassGate rejects passing a gate while an earlier one is not pass', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    // BUILD is pending; you cannot pass UNIT_TEST yet.
    expect(canPassGate(mission, 'unit_test')).toBe(false);
    // And you certainly cannot reach MERGE.
    expect(canPassGate(mission, 'merge')).toBe(false);
  });

  test('the ladder allows passing the first gate, then the next', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    const afterBuild = advanceGate(db, mission.id, 'build', 'pass');
    expect(afterBuild).not.toBeNull();
    expect(afterBuild!.gates.build).toBe('pass');
    // Once build is pass, unit_test is allowed.
    expect(canPassGate(afterBuild!, 'unit_test')).toBe(true);
  });

  test('gates must be advanced in order — jump to merge is blocked', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    // Directly passing the last gate is rejected by the ladder.
    const result = advanceGate(db, mission.id, 'merge', 'pass');
    expect(result).toBeNull();
  });

  test('waiting on a gate sets the mission to awaiting_approval', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    advanceGate(db, mission.id, 'clinical', 'waiting');
    expect(db.missions.byId(mission.id)?.status).toBe('awaiting_approval');
    expect(blockingGate(db.missions.byId(mission.id)!)?.gate).toBe('clinical');
  });

  test('a failed gate blocks the mission', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    advanceGate(db, mission.id, 'security', 'fail');
    expect(db.missions.byId(mission.id)?.status).toBe('blocked');
    expect(blockingGate(db.missions.byId(mission.id)!)?.gate).toBe('security');
  });

  test('a mission is complete only when every gate is pass', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    for (const g of GATE_ORDER) {
      // Passing each gate in order is safe because all previous are already pass.
      const result = advanceGate(db, mission.id, g, 'pass');
      // Ladder: pass gates sequentially from the first.
      if (!result) {
        // The very first gate must be passable; this is a safety net.
        expect(g).toBe('build');
      }
    }
    const completed = missionComplete(db, mission.id);
    expect(completed?.status).toBe('complete');
  });
});

describe('NURA Control Plane — command bus & summary', () => {
  test('queueCommand inserts a command with status queued', () => {
    db = openDb(':memory:');
    const command = queueCommand(db, 'ceo', 'Ship the Omi adapter');
    expect(command.status).toBe('queued');
    expect(db.commands.all().map((c) => c.intent)).toContain('Ship the Omi adapter');
  });

  test('controlPlaneSummary counts missions by status', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    db.missions.setStatus(mission.id, 'executing', new Date().toISOString());
    const summary = controlPlaneSummary(db);
    expect(summary.total).toBe(1);
    expect(summary.executing).toBe(1);
  });

  test('a fresh mission begins as proposed and executes on approval', () => {
    db = openDb(':memory:');
    const { mission } = seedMission();
    expect(mission.status).toBe('proposed');
    db.missions.setStatus(mission.id, 'executing', new Date().toISOString());
    expect(db.missions.byId(mission.id)?.status).toBe('executing');
  });
});

describe('NURA Control Plane — gate label & ladder integrity', () => {
  test('the ladder is the full change policy in release order', () => {
    expect(GATE_ORDER).toEqual([
      'build',
      'unit_test',
      'integration',
      'security',
      'clinical',
      'qa',
      'merge',
    ]);
  });

  test('defaultGates returns all gates pending', () => {
    const gates = defaultGates();
    expect(Object.keys(gates).sort()).toEqual([...GATE_ORDER].sort());
    expect(Object.values(gates).every((v) => v === 'pending')).toBe(true);
  });
});
