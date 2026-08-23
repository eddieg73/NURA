import asyncio
import json
from typing import Any, Dict
from backend.plugins.core_plugins import EHRPlugin
from backend.plugins.scribe_plugin import ScribePlugin

class OrionGenUI:
    """Simulates the GenUI rendering engine for the Flutter frontend."""
    def render(self, component_type: str, data: Any):
        if component_type == "SOAP_CARD":
            return f"[UI: SOAP_CARD] $\\nS: {data['subjective']}\\nO: {data['objective']}\\nA: {data['assessment']}\\nP: {data['plan']}"
        elif component_type == "ALERT_BANNER":
            return f"[UI: ALERT_BANNER] 🚨 {data['message']} | Action: {data['action']}"
        elif component_type == "DATA_TABLE":
            return f"[UI: DATA_TABLE] Headers: {data['headers']} | Rows: {data['rows']}"
        return f"[UI: GENERIC] {data}"

async def run_scribe_workflow():
    # 1. Setup
    scribe = ScribePlugin({"B2_BUCKET": "nura-emh-backups"})
    ui = OrionGenUI()
    
    print("🎤 Starting Ambient Scribe Workflow...")
    
    # 2. Execute la-Scribe
    result = await scribe.execute({
        "action": "process_audio", 
        "audio_url": "s3://nura-audio/encounter_001.wav"
    })
    
    # 3. Render via GenUI (This is what the Flutter app would do)
    print("\n--- Frontend Rendering (GenUI) ---")
    rendered_note = ui.render("SOAP_CARD", result.data["soap"])
    print(rendered_note)
    print(f"Audit Trail ID: {result.audit_id}")

if __name__ == "__main__":
    asyncio.run(run_scribe_workflow())
