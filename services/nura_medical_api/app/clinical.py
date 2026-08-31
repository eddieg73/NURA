from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx
from pydantic import ValidationError

from .config import Settings
from .schemas import ClinicalOutput, ProvenanceItem


SYSTEM_INSTRUCTIONS = """
You are a clinician decision-support drafting service. You do not establish a diagnosis,
issue treatment orders, or replace the accountable clinician. Work only from supplied
case text. Separate source facts from interpretation. Return one JSON object with exactly
these keys: source_facts, interpretation, differential, dangerous_alternatives, red_flags,
missing_data, recommended_next_step, urgency, confidence, evidence_as_of, limitations,
provenance. differential must be an array of objects with label, support, confidence.
urgency must be routine, urgent, emergent, or undetermined. confidence must be low,
medium, or high. State uncertainty and missing information. Never invent a finding,
measurement, medication, test result, citation, or guideline. The output is a DRAFT that
requires licensed-clinician review.
""".strip()


@dataclass(frozen=True)
class ProviderResult:
    output: ClinicalOutput
    provider_name: str
    model_name: str | None


class ClinicalProvider(ABC):
    @abstractmethod
    async def generate(self, operation: str, case_text: str, evidence_as_of: str) -> ProviderResult:
        raise NotImplementedError


class DisabledProvider(ClinicalProvider):
    async def generate(self, operation: str, case_text: str, evidence_as_of: str) -> ProviderResult:
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+|\n+", case_text)
            if sentence.strip()
        ][:20]
        operation_note = {
            "scribe": "A structured clinical note was requested, but inference is disabled.",
            "dx": "Diagnostic decision support was requested, but inference is disabled.",
            "synthesis": "Clinical synthesis was requested, but inference is disabled.",
        }.get(operation, "Clinical drafting was requested, but inference is disabled.")
        return ProviderResult(
            provider_name="disabled-safe-mode",
            model_name=None,
            output=ClinicalOutput(
                source_facts=sentences,
                interpretation=operation_note,
                differential=[],
                dangerous_alternatives=[],
                red_flags=[],
                missing_data=[
                    "No model or approved clinical-engine provider is enabled.",
                    "The accountable clinician must independently review the source text.",
                ],
                recommended_next_step="Review the source facts and complete the clinical assessment manually.",
                urgency="undetermined",
                confidence="low",
                evidence_as_of=evidence_as_of,
                limitations=[
                    "Inference disabled by deployment policy.",
                    "No external evidence retrieval was performed.",
                    "Not for autonomous diagnosis or treatment.",
                ],
                provenance=[ProvenanceItem(source_type="user_provided_case_text")],
            ),
        )


class HermesProvider(ClinicalProvider):
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, operation: str, case_text: str, evidence_as_of: str) -> ProviderResult:
        assert self.settings.clinical_engine_url
        headers = {"Content-Type": "application/json"}
        if self.settings.clinical_engine_token:
            headers["Authorization"] = f"Bearer {self.settings.clinical_engine_token}"
        payload = {
            "operation": operation,
            "case_text": case_text,
            "evidence_as_of": evidence_as_of,
            "output_contract": "nura-clinical-draft-v1",
            "provider_approval_required": True,
        }
        async with httpx.AsyncClient(timeout=self.settings.clinical_request_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.clinical_engine_url.rstrip('/')}/v1/clinical/draft",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
        candidate = body.get("output", body)
        return ProviderResult(
            output=ClinicalOutput.model_validate(candidate),
            provider_name="hermes-clinical-engine",
            model_name=body.get("model"),
        )


class OpenAIProvider(ClinicalProvider):
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, operation: str, case_text: str, evidence_as_of: str) -> ProviderResult:
        assert self.settings.openai_api_key
        payload = {
            "model": self.settings.openai_model,
            "store": False,
            "input": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "operation": operation,
                            "case_text": case_text,
                            "evidence_as_of": evidence_as_of,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.settings.clinical_request_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.openai_base_url.rstrip('/')}/responses",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            body = response.json()

        text = body.get("output_text") or _extract_responses_text(body)
        candidate = _parse_json_object(text)
        try:
            output = ClinicalOutput.model_validate(candidate)
        except ValidationError as exc:
            raise RuntimeError("AI response failed the NURA clinical output contract") from exc
        output.provenance.append(
            ProvenanceItem(source_type="model_draft", source_id=str(body.get("id", "")))
        )
        return ProviderResult(
            output=output,
            provider_name="openai-responses-api",
            model_name=self.settings.openai_model,
        )


def _extract_responses_text(body: dict) -> str:
    parts: list[str] = []
    for item in body.get("output", []):
        for content in item.get("content", []):
            text_value = content.get("text")
            if isinstance(text_value, str):
                parts.append(text_value)
    if not parts:
        raise RuntimeError("Clinical model returned no text output")
    return "\n".join(parts)


def _parse_json_object(text_value: str) -> dict:
    cleaned = text_value.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise RuntimeError("Clinical model did not return JSON") from exc
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise RuntimeError("Clinical model output must be a JSON object")
    return value


def build_provider(settings: Settings) -> ClinicalProvider:
    if settings.ai_provider == "openai":
        return OpenAIProvider(settings)
    if settings.ai_provider == "hermes":
        return HermesProvider(settings)
    return DisabledProvider()
