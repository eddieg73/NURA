import { NextResponse } from 'next/server';
import { getDb } from '@/lib/data';
import { decideApproval, pendingApprovals } from '@/lib/governance';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

/** The governed approval inbox — open approvals awaiting a human decision. */
export async function GET() {
  const db = getDb();
  return NextResponse.json({ approvals: pendingApprovals(db) });
}

/** Decide an open approval. Records the approver + rationale, and applies the
 *  consequence to the mission gate (approved -> pass, rejected -> fail). */
export async function POST(req: Request) {
  const db = getDb();
  let body: { approvalId?: string; decision?: 'approved' | 'rejected'; actor?: string; rationale?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON body' }, { status: 400 });
  }
  if (!body.approvalId) {
    return NextResponse.json({ error: 'approvalId is required' }, { status: 400 });
  }
  if (body.decision !== 'approved' && body.decision !== 'rejected') {
    return NextResponse.json({ error: "decision must be 'approved' | 'rejected'" }, { status: 400 });
  }
  const actor = body.actor?.trim() || 'operator';
  const result = decideApproval(db, body.approvalId, body.decision, actor, body.rationale ?? '');
  if (!result.approval) {
    return NextResponse.json({ error: 'unknown approval' }, { status: 404 });
  }
  if (result.error) {
    // decided already, or evidence-missing on an approve
    return NextResponse.json({ approval: result.approval, mission: result.mission, error: result.error }, { status: result.error === 'unknown approval' ? 404 : 409 });
  }
  return NextResponse.json({ approval: result.approval, mission: result.mission });
}
