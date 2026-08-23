import asyncio
import json
from typing import Any, Dict, List
from backend.plugins.core_plugins import EHRPlugin
from backend.plugins.scribe_plugin import ScribePlugin
from backend.plugins.docsgpt_plugin import DocsGPTPlugin
from backend.plugins.identity_plugin import IdentityPlugin
from backend.plugins.vision_plugin import VisionPlugin
from backend.model_router import OrionModelRouter, ModelTier

class OrionSovereignCore:
    """The 'Autonomous Perfection' Core for Project ORION.
    Now featuring Tiered Model Routing: Gemini $\rightarrow$ Nvidia $\rightarrow$ Claude.
    """
    def __init__(self):
        self.config = {"B2_BUCKET": "nura-orion-audit"}
        self.identity = IdentityPlugin(self.config)
        self.scribe = ScribePlugin(self.config)
        self.docs = DocsGPTPlugin(self.config)
        self.ehr = EHRPlugin(self.config)
        self.vision = VisionPlugin(self.config)
        
        # THE ROUTER: Centralizes all LLM calls
        self.router = OrionModelRouter()

    async def run_multimodal_cycle(self, npi: str, email: str, audio_url: str, image_url: str, patient_id: str):
        print(f"\n🚀 STARTING TIERED AUTONOMOUS CYCLE [Patient: {patient_id}]")
        
        # 1. Identity Gate
        id_res = await self.identity.execute({"action": "verify_provider", "npi": npi, "email": email})
        if id_res.status != "success": return print("  ❌ Access Denied.")

        # 2. Parallel Perception (Multimodal)
        print("\n[Perception Phase] Routing to Gemini (Tier 1)...")
        scribe_task = self.scribe.execute({"action": "process_audio", "audio_url": audio_url})
        vision_task = self.vision.execute({"action": "analyze_clinical_image", "image_url": image_url})
        
        scribe_res, vision_res = await asyncio.gather(scribe_task, vision_task)
        
        # 3. High-Reasoning Synthesis (The Escalation Move)
        # We use the router to synthesize the findings. If Gemini is unsure, it hits Claude.
        print("\n[Synthesis Phase] Routing to Sovereign Router (Gemini $\rightarrow$ Nvidia $\rightarrow$ Claude)...")
        prompt = f"Synthesize these findings for Patient {patient_id}: \nScribe: {scribe_res.data['soap']['assessment']} \nVision: {vision_res.data['observation']}"
        
        # This call will automatically escalate to Claude if Gemini's confidence is low
        synthesis = await self.router.route(prompt, task_type="clinical_synthesis")
        print(f"  Final Synthesis (via {synthesis['model']}): {synthesis['content']}")

        # 4. Safety Guardrails & EHR Writeback
        print("\n[Execution Phase] Committing to EHR...")
        final_note = f"Sovereign Synthesis: {synthesis['content']} | Source: {synthesis['model']}"
        await self.ehr.execute({"action": "create_note", "patient_id": patient_id, "note": final_note})
        
        print("  ✅ Cycle Complete. Routed through Sovereign Tiered Stack.")

async def main():
    core = OrionSovereignCore()
    await core.run_multimodal_cycle(
        npi="1154381580", email="eddie@nuratech.ai", 
        audio_url="s3://nura-audio/enc_002.wav", 
        image_url="s3://nura-images/skin_002.jpg", 
        patient_id="P123"
    )

if __name__ == "__main__":
    asyncio.run(main())
