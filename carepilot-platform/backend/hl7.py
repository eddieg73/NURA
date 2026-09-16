"""HL7 v2.x ADT parsing -> TCM event trigger.
Parses the segments Mirth NextGen Connect delivers (MSH/PID/PV1/EVN) for
ADT^A01 (admit) / ADT^A03 (discharge) / ADT^A04-A06 (er/transfer), extracts the
patient identifier + event type, and maps it to a TCM event intake.
Deterministic, propose-only (it only OPENS a case + alerts the team; it never
signs/orders/diagnoses). Parity with the Mirth NURA-Bridge HL7 contract.
"""
import re
from typing import Optional, Dict

# HL7 segment field separators (pipe + component + repetition)
SEP_PIPE = "|"
SEP_COMPONENT = "^"
SEP_REPEAT = "~"

_ADT_ADMIT = {"A01", "A04"}     # admit / a04 unknown type (treat as admit)
_ADT_DISCHARGE = {"A03"}        # discharge
_ADT_ER = {"A04"}               # note: A04 is technically admit; ER handled by source


def _field(seg: str, idx: int) -> str:
    """Return the idx-th field of a pipe-delimited segment (1-based, MSH offset)."""
    parts = seg.split(SEP_PIPE)
    # MSH has an extra leading empty because of the | separators, so index is shifted
    return parts[idx] if len(parts) > idx else ""


def parse_adt(message: str) -> Optional[Dict]:
    """Parse an HL7 v2.x ADT message into {event, patient_ref, source, facility, ts}."""
    if not message or not message.strip():
        return None
    segments = [s for s in message.split("\r") if s.strip()]
    if not segments:
        segments = [s for s in message.split("\n") if s.strip()]

    msh = next((s for s in segments if s.startswith("MSH")), "")
    pid = next((s for s in segments if s.startswith("PID")), "")
    pv1 = next((s for s in segments if s.startswith("PV1")), "")
    evn = next((s for s in segments if s.startswith("EVN")), "")

    # message type from MSH-9 (e.g. ADT^A01). Split: [0]=MSH [1]=^~\& [2..7]=app/facility/ts [8]=MSH-9 [9]=MSH-10 ctrl
    msh_parts = msh.split(SEP_PIPE)
    msg_type_full = ""
    if len(msh_parts) > 8:
        msg_type_full = msh_parts[8]  # MSH-9
    event_code = (msg_type_full.split(SEP_COMPONENT)[1] if SEP_COMPONENT in msg_type_full
                  else msg_type_full.split(SEP_REPEAT)[0])

    # patient id from PID-3 (pid id list: <id>^^^<id type>). Split: [0]=PID [1]=set [2]=pid2 [3]=PID-3 [5]=PID-5 name
    p3 = pid.split(SEP_PIPE)
    mrn = ""
    if len(p3) > 3:
        pid3 = p3[3]
        for comp in pid3.split(SEP_COMPONENT):
            if comp:
                mrn = comp
                break
    patient_ref = mrn

    # facility from PV1-3 (assigned patient location) or MSH-4
    pv1_parts = pv1.split(SEP_PIPE)
    # PV1 split: [0]=PV1 [1]=set [2]=class [3]=PV1-3 location [4]=PV1-4 admit-type
    location = pv1_parts[3].split(SEP_COMPONENT)[0] if len(pv1_parts) > 3 else ""  # PV1-3
    facility = location or (msh_parts[3] if len(msh_parts) > 3 else "")  # MSH-4

    # event mapping
    event = "admit"
    if event_code in _ADT_DISCHARGE:
        event = "discharge"
    elif event_code in _ADT_ER or event_code in {"A05", "A06"}:
        event = "er_visit"
    elif event_code in _ADT_ADMIT:
        event = "admit"

    return {"event": event, "event_code": event_code, "patient_ref": patient_ref,
            "source": "mirth_adt", "facility": facility, "msg_type": msg_type_full}


# A tiny helper to render a canonical test ADT message.
def adt_example(event_type="ADT^A01", mrn="MRN-001", facility="Broward General"):
    ts = "20260907090000"
    msh = f"MSH|^~\\&|EMR|{facility}|MIRTH|FACILITY|{ts}||{event_type}|MSG12345|P|2.5"
    evn = f"EVN|{event_type.split('^')[1]}|{ts}"
    pid = f"PID|1||{mrn}^^^MR^MRN||Cleo Torres||1985-01-01|F"
    pv1 = f"PV1|1|I|METRO^1^1|E||||||||||||||||||||||||||||||||"
    return "\r".join([msh, evn, pid, pv1])
