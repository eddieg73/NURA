import asyncio
import json
import uuid
from typing import Any, Dict, List
from backend.plugins.core_plugins import EHRPlugin
from backend.plugins.scribe_plugin import ScribePlugin
from backend.plugins.docsgpt_plugin import DocsGPTPlugin

class OrionClinicalOrchestrator:
    """The high-level coordinator for the Invisible Assistant workflow.
    Flow: Ambient Audio -> Scribe (SOAP) -> DocsGPT (Guideline) -> EHR (Draft Order).
    """
    def __init__(self):
        self.config = {"B2_BUCKET": "nura-orion-audit"}
        self.scribe = ScribePlugin(self.config)
        self.docs = DocsGPTPlugin(self.config)
        self.ehr = EHRPlugin(self.config)
        self.ui = OrionGenUI()

    async def handle_encounter(self, audio_url: str, patient_id: str):
        print(f"🚀 STARTING CLINICAL CHAIN for Patient {patient_id}...")
        
        # 1. The Scribe Lane: Audio -> SOAP
        print("\n[Step 1: Scribing]")
        scribe_res = await self.scribe.execute({"action": "process_audio", "audio_url": audio_url})
        soap = scribe_res.data["soap"]
        print(f"  Scribe Complete: {soap['assessment']}")

        # 2. The Knowledge Lane: Assessment -> Guideline
        print("\n[Step 2: Knowledge Retrieval]")
        # We use the 'assessment' from the scribe to query the guidelines
        guideline_res = await self.docs.execute({
            "action": "query_docs", 
            "query": f"Gold standard treatment for {soap['assessment']}",
            "context": soap['subjective']
        })
        guideline = guideline_res.data["answer"]
        print(f"  Guideline found: {guideline[:100]}...")

        # 3. The EHR Lane: Guideline -> Draft Order
        print("\n[Step 3: Order Drafting]")
        # Draft the order based on the guideline
        order_note = f"Based on current guidelines: {guideline}. Ordering: ECG, Troponins."
        ehr_res = await self.ehr.execute({
            "action": "create_note", 
            "patient_id": patient_id, 
            "note": order_note
        })
        print(f"  EHR Draft Complete: {ehr_res.data['status']} | Audit ID: {ehr_res.audit_id}")

        # 4. The GenUI Render: Chain -> UI
        print("\n--- FINAL GENUI PAYLOAD ---")
        payload = {
            "components": [
                {"type": "SOAP_CARD", "data": soap},
                {"type": "KNOWLEDGE_CARD", "data": {"answer": guideline, "sources": guideline_res.data["sources"]}},
                {"type": "ORDER_CONFIRMATION", "data": {"note_id": ehr_res.data['note_id'], "content": order_note}}
            ]
        }
        print(json.dumps(payload, indent=2))
        return payload

class OrionGenUI:
    """GenUI Renderer for simulation."""
    def render(self, component_type: str, data: Any):
        # (Same logic as previous genui_test.py)
        return f"[UI: {component_type}] {data}"

async def main():
    orch = OrionClinicalOrchestrator()
    await orch.handle_encounter(
        audio_url="s3://nura-audio/encounter_001.wav", 
        patient_id="P123"
    )

if __name__ == "__main__":
    asyncio.run(main())
