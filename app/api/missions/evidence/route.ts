import { NextResponse } from 'next/server';
import { getDb } from '@/lib/data';
import { attachEvidence } from '@/lib/governance';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

/** Bind a concrete evidence handle (build id / test run / review / commit SHA) to
 *  a mission so its gates can pass under the evidence-before-pass rule. Emission
 *  is audited by governance.ts. */
export async function POST(req: Request) {
  const db = getDb();
  let body: { missionId?: string; evidence?: string; actor?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON body' }, { status: 400 });
  }
  if (!body.missionId || !body.evidence?.trim()) {
    return NextResponse.json({ error: 'missionId and a non-empty evidence handle are required' }, { status: 400 });
  }
  try {
    const mission = attachEvidence(db, body.missionId, body.evidence, body.actor?.trim() || 'operator');
    return NextResponse.json({ mission });
  } catch (e) {
    return NextResponse.json({ error: e instanceof Error ? e.message : 'failed to attach evidence' }, { status: 400 });
  }
}
