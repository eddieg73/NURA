import { NextResponse } from 'next/server';
import { getDb } from '@/lib/data';
import { advanceGateGoverned } from '@/lib/governance';
import { blockingGate, missionComplete } from '@/lib/control-plane';
import { GATE_ORDER, type GateId, type GateStatus } from '@/lib/schemas';

export const dynamic = 'force-dynamic';

/**
 * Advance one gate on a mission UNDER GOVERNANCE. Enforces the evidence-before-pass
 * rule (a `pass` requires the mission to carry evidence) and writes the immutable
 * audit event for every transition — including denials. Passing any gate still
 * requires the earlier ladder steps to be pass.
 */
export async function POST(req: Request) {
  const db = getDb();
  let body: { missionId?: string; gate?: string; status?: string; actor?: string };
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

  const actor = body.actor?.trim() || 'operator';
  const res = advanceGateGoverned(db, missionId, gate as GateId, status as GateStatus, actor);
  if (!res.mission) {
    return NextResponse.json(
      { error: missionId && !db.missions.byId(missionId) ? 'unknown mission' : 'gate blocked by an earlier step in the ladder' },
      { status: missionId && !db.missions.byId(missionId) ? 404 : 409 },
    );
  }

  // Evidence-before-pass denial is a 409 with the reason; the mission is unchanged.
  if (res.denial) {
    return NextResponse.json({ mission: res.mission, denial: res.denial }, { status: 409 });
  }

  const completed = missionComplete(db, missionId);
  return NextResponse.json({ mission: completed ?? res.mission, blockingGate: blockingGate(completed ?? res.mission) });
}
