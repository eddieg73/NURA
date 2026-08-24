import { NextResponse } from 'next/server';
import { getDb } from '@/lib/data';
import { missionAudit } from '@/lib/governance';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

/** Replayable audit trail for one mission (newest first). */ 
export async function GET(req: Request) {
  const missionId = new URL(req.url).searchParams.get('missionId');
  const db = getDb();
  if (missionId) {
    return NextResponse.json({ events: missionAudit(db, missionId) });
  }
  // No mission filter — the recent cross-mission ledger.
  return NextResponse.json({ events: db.events.recent(100) });
}
