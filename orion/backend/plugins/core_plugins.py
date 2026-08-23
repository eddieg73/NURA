import os
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import requests

class PluginResponse(BaseModel):
    status: str = Field(..., description="success or error")
    data: Any = Field(..., description="The actual result of the execution")
    audit_id: str = Field(..., description="ID of the log entry in B2")

class OrionPlugin:
    """Base class for all ORION plug-ins."""
    def __init__(self, config: Dict):
        self.config = config
        self.audit_bucket = config.get("B2_BUCKET", "nura-orion-audit")

    async def _log_to_audit(self, action: str, params: Dict, result: Any) -> str:
        audit_id = f"audit_{uuid.uuid4().hex[:12]}"
        log_entry = {
            "audit_id": audit_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "params": params,
            "result": result,
            "status": "verified"
        }
        # In production, this pushes to B2. For smoke test, we write to local audit log.
        with open("/opt/data/nura_medical/orion/audit/audit.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        return audit_id

    async def describe(self) -> Dict:
        raise NotImplementedError("Plugins must implement describe()")

    async def execute(self, params: Dict) -> PluginResponse:
        raise NotImplementedError("Plugins must implement execute()")

    async def status(self) -> Dict:
        return {"status": "online", "version": "1.0.0"}

class EHRPlugin(OrionPlugin):
    """OpenEMR Integration Plug-in"""
    async def describe(self) -> Dict:
        return {
            "name": "ehr_plugin",
            "description": "Accesses OpenEMR for patient records and notes",
            "tools": {
                "get_patient": {"params": {"patient_id": "str"}, "desc": "Fetch patient summary"},
                "create_note": {"params": {"patient_id": "str", "note": "str"}, "desc": "Draft a clinical note"}
            }
        }

    async def execute(self, params: Dict) -> PluginResponse:
        action = params.get("action")
        p_id = params.get("patient_id")
        
        if action == "get_patient":
            # Mocking the API call to OpenEMR for the smoke test
            # Real call would use requests.get(f"{self.config['URL']}/patient/{p_id}", auth=...)
            data = {"patient_id": p_id, "name": "Jane Doe", "history": "Hypertension, Type 2 Diabetes", "last_visit": "2026-08-10"}
            audit_id = await self._log_to_audit("get_patient", params, data)
            return PluginResponse(status="success", data=data, audit_id=audit_id)
        
        elif action == "create_note":
            note = params.get("note")
            data = {"status": "drafted", "note_id": "note_123"}
            audit_id = await self._log_to_audit("create_note", params, data)
            return PluginResponse(status="success", data=data, audit_id=audit_id)
            
        return PluginResponse(status="error", data="Unknown action", audit_id="none")
