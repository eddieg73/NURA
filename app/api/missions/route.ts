import { NextResponse } from 'next/server';
import { getDb } from '@/lib/data';
import { controlPlaneSummary, decomposeCommand, queueCommand } from '@/lib/control-plane';

export const dynamic = 'force-dynamic';

/** Mission Control feed: all missions + the header aggregate + recent commands. */
export async function GET() {
  const db = getDb();
  return NextResponse.json({
    summary: controlPlaneSummary(db),
    missions: db.missions.all(),
    commands: db.commands.all(),
  });
}

/** Queue an executive command. It becomes a mission (owned by the CTO) and is
 *  dispatched to the runtime; FounderOS only routes it, it does not execute. */
export async function POST(req: Request) {
  const db = getDb();
  let body: { intent?: string; source?: string; priority?: 'P0' | 'P1' | 'P2' | 'P3' };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON body' }, { status: 400 });
  }
  if (!body.intent || !body.intent.trim()) {
    return NextResponse.json({ error: 'intent is required' }, { status: 400 });
  }
  const source = body.source || 'operator';
  const command = queueCommand(db, source, body.intent);
  const mission = decomposeCommand(db, { source, intent: body.intent }, { priority: body.priority });
  db.commands.setStatus(command.id, 'dispatched');
  db.commands.insert({ ...command, missionId: mission.id, status: 'dispatched' });
  return NextResponse.json({ command, mission }, { status: 201 });
}
