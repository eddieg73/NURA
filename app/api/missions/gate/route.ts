import { NextResponse } from 'next/server';
import { getDb } from '@/lib/data';
import { advanceGate, blockingGate, missionComplete } from '@/lib/control-plane';
import { GATE_ORDER, type GateId, type GateStatus } from '@/lib/schemas';

export const dynamic = 'force-dynamic';

/**
 * Advance one gate on a mission. Enforces the change-policy ladder: you cannot
 * pass a gate while an earlier gate is not `pass`. A `waiting` status arms the
 * approval (mission → awaiting_approval); a `fail` blocks it.
 */
export async function POST(req: Request) {
  const db = getDb();
  let body: { missionId?: string; gate?: string; status?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON body' }, { status: 400 });
  }
  const { missionId, gate, status } = body;
  if (!missionId || !gate || !status) {
    return NextResponse.json({ error: 'missionId, gate, and status are required' }, { status: 400 });
  }
  if (!(GATE_ORDER as readonly string[]).includes(gate)) {
    return NextResponse.json({ error: `gate must be one of: ${GATE_ORDER.join(', ')}` }, { status: 400 });
  }
  if (!['pending', 'pass', 'review', 'waiting', 'fail'].includes(status)) {
    return NextResponse.json({ error: 'status must be pending | pass | review | waiting | fail' }, { status: 400 });
  }

  const mission = advanceGate(db, missionId, gate as GateId, status as GateStatus);
  if (!mission) {
    return NextResponse.json(
      { error: missionId && !db.missions.byId(missionId) ? 'unknown mission' : 'gate blocked by an earlier step in the ladder' },
      { status: missionId && !db.missions.byId(missionId) ? 404 : 409 },
    );
  }

  // If this pass completed the pipeline, mark the mission complete.
  const completed = missionComplete(db, missionId);
  return NextResponse.json({ mission: completed ?? mission, blockingGate: blockingGate(completed ?? mission) });
}
