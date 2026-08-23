import { randomUUID } from 'node:crypto';
import type { FounderDb } from '@/lib/db';
import {
  GATE_ORDER,
  MissionStatusSchema,
  type Command,
  type GateId,
  type GateStatus,
  type Mission,
  type MissionPriority,
  type MissionTask,
} from '@/lib/schemas';

/**
 * NURA Control Plane — the seam between the command-center UI (eyes/controls)
 * and the Hermes runtime (brain/hands).
 *
 * FounderOS never becomes an autonomous agent. It accepts executive commands
 * and routes the work; Hermes (or a worker agent) decomposes and executes. This
 * module owns the lifecycle semantics: missions, tasks, the gate pipeline, and
 * the change policy that decides whether work may merge.
 */

// Default gate ladder for a freshly-created mission. All pending; the mission
// advances as the gates are proven. This is the change-policy order visible on
// the dashboard (BUILD → UNIT → INTEGRATION → SECURITY → CLINICAL → QA → MERGE).
export function defaultGates(): Record<GateId, GateStatus> {
  return Object.fromEntries(GATE_ORDER.map((g) => [g, 'pending'])) as Record<GateId, GateStatus>;
}

/** Human-facing label for a gate id. */
export const GATE_LABELS: Record<GateId, string> = {
  build: 'Build',
  unit_test: 'Unit test',
  integration: 'Integration',
  security: 'Security',
  clinical: 'Clinical',
  qa: 'QA',
  merge: 'Merge',
};

/** Where each gate sits in the change-policy ladder (0 = first). */
export const GATE_RANK: Record<GateId, number> = Object.fromEntries(
  GATE_ORDER.map((g, i) => [g, i]),
) as Record<GateId, number>;

/**
 * Is the mission allowed to advance past the given gate?
 * Returns false if ANY earlier gate is not `pass`. This enforces the ladder:
 * you cannot reach MERGE with a failing SECURITY gate above it.
 */
export function canPassGate(mission: Mission, gate: GateId): boolean {
  const gateRank = GATE_RANK[gate];
  for (const [g, status] of Object.entries(mission.gates) as [GateId, GateStatus][]) {
    if (g === gate) continue;
    if (GATE_RANK[g] < gateRank && status !== 'pass') return false;
  }
  return true;
}

/**
 * The gate that is currently blocking a mission, if any. Returns the first
 * gate (in ladder order) that is `fail` or `waiting`. `null` when the mission
 * can advance.
 */
export function blockingGate(mission: Mission): { gate: GateId; status: GateStatus } | null {
  for (const g of GATE_ORDER) {
    const status = mission.gates[g];
    if (status === 'fail' || status === 'waiting') return { gate: g, status };
  }
  return null;
}

/**
 * Decompose an executive command into a mission owned by the CTO. The command
 * is the raw intent; this produces the mission object plus its initial task
 * breakdown. The CTO (or a worker) fulfils the tasks — the UI only routes them.
 */
export function decomposeCommand(
  db: FounderDb,
  command: { source: string; intent: string },
  opts: { priority?: MissionPriority; ownerAgentId?: string } = {},
): Mission {
  const now = new Date().toISOString();
  const id = `mission-${randomUUID().slice(0, 8)}`;
  const priority = opts.priority ?? 'P1';
  const ownerAgentId = opts.ownerAgentId ?? 'hermes-cto';

  const tasks: MissionTask[] = [
    {
      id: `${id}-t1`,
      title: 'Inspect repository & existing work',
      ownerAgentId: 'software-architect',
      status: 'pending',
      order: 0,
    },
    {
      id: `${id}-t2`,
      title: 'Create architecture & schemas',
      ownerAgentId: 'software-architect',
      status: 'pending',
      order: 1,
    },
    {
      id: `${id}-t3`,
      title: 'Implement core features',
      ownerAgentId: 'backend-engineer',
      status: 'pending',
      order: 2,
    },
    {
      id: `${id}-t4`,
      title: 'Write tests',
      ownerAgentId: 'qa',
      status: 'pending',
      order: 3,
    },
    {
      id: `${id}-t5`,
      title: 'Security review',
      ownerAgentId: 'cybersecurity',
      status: 'pending',
      order: 4,
    },
    {
      id: `${id}-t6`,
      title: 'Clinical safety review (if applicable)',
      ownerAgentId: 'clinical-intelligence',
      status: 'pending',
      order: 5,
    },
    {
      id: `${id}-t7`,
      title: 'Documentation',
      ownerAgentId: 'research',
      status: 'pending',
      order: 6,
    },
    {
      id: `${id}-t8`,
      title: 'Deploy to staging',
      ownerAgentId: 'devops',
      status: 'pending',
      order: 7,
    },
  ];

  const mission: Mission = {
    id,
    mission: command.intent,
    priority,
    ownerAgentId,
    status: 'proposed',
    dependencies: [],
    approvalsRequired: [],
    artifacts: [],
    tests: [],
    risks: [],
    evidence: [],
    gates: defaultGates(),
    tasks,
    createdAt: now,
    updatedAt: now,
  };

  db.missions.insert(mission);
  return mission;
}

/** Queue a command on the bus. Does not execute — the runtime fulfils it. */
export function queueCommand(db: FounderDb, source: string, intent: string): Command {
  const now = new Date().toISOString();
  const command: Command = {
    id: randomUUID(),
    source,
    intent,
    missionId: null,
    status: 'queued',
    createdAt: now,
  };
  db.commands.insert(command);
  return command;
}

/** Link a queued command to the mission it produced, and mark it dispatched. */
export function dispatchCommand(db: FounderDb, commandId: string, missionId: string): void {
  db.commands.setStatus(commandId, 'dispatched');
  const command = db.commands.all().find((c) => c.id === commandId);
  if (command) {
    db.commands.insert({ ...command, missionId });
  }
}

/** Aggregate view for the Mission Control dashboard header. */
export function controlPlaneSummary(db: FounderDb) {
  const missions = db.missions.all();
  return {
    total: missions.length,
    executing: missions.filter((m) => m.status === 'executing').length,
    awaitingApproval: missions.filter((m) => m.status === 'awaiting_approval').length,
    blocked: missions.filter((m) => m.status === 'blocked').length,
    complete: missions.filter((m) => m.status === 'complete').length,
    proposed: missions.filter((m) => m.status === 'proposed').length,
  };
}

/** Reset a mission to `executing` once its approvals are granted. */
export function beginExecution(db: FounderDb, missionId: string): Mission | null {
  const mission = db.missions.byId(missionId);
  if (!mission) return null;
  MissionStatusSchema.parse('executing');
  db.missions.setStatus(missionId, 'executing', new Date().toISOString());
  return db.missions.byId(missionId);
}

/** Record hard evidence against a mission (a build id, test output, review). */
export function attachEvidence(db: FounderDb, missionId: string, evidence: string): Mission | null {
  db.missions.addEvidence(missionId, evidence, new Date().toISOString());
  return db.missions.byId(missionId);
}

/**
 * Advance one gate for a mission. Enforces the ladder: if an earlier gate is
 * not `pass`, the request is rejected (returns null). Otherwise sets the gate
 * to the requested status and returns the updated mission.
 */
export function advanceGate(
  db: FounderDb,
  missionId: string,
  gate: GateId,
  status: GateStatus,
): Mission | null {
  const mission = db.missions.byId(missionId);
  if (!mission) return null;
  if (status === 'pass' && !canPassGate(mission, gate)) return null;
  db.missions.setGate(missionId, gate, status, new Date().toISOString());
  return db.missions.byId(missionId);
}

export function missionComplete(db: FounderDb, missionId: string): Mission | null {
  const mission = db.missions.byId(missionId);
  if (!mission) return null;
  const allPass = GATE_ORDER.every((g) => mission.gates[g] === 'pass');
  if (allPass) db.missions.setStatus(missionId, 'complete', new Date().toISOString());
  return db.missions.byId(missionId);
}
