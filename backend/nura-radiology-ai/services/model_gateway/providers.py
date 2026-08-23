"""Model providers — OpenAI/Anthropic-compatible adapters behind the gateway.
All runtime models implement reason() -> dict. The StubProvider is deterministic (no network)
so the gateway logic can be verified and run in dev without model tokens."""
import os, json, logging

logger = logging.getLogger("nura.gateway.providers")


class BaseProvider:
    name = "base"

    def reason(self, payload: dict) -> dict:
        raise NotImplementedError


class StubProvider(BaseProvider):
    """Deterministic reasoning provider for dev/verification. No tokens, no network."""
    name = "stub"
    def __init__(self, output=None, fail=False):
        self._output = output
        self._fail = fail
    def reason(self, payload):
        if self._fail:
            raise RuntimeError("stub provider forced failure")
        return self._output if self._output is not None else {"interpretation": {"status": "abnormal", "summary": "stub"}}


class OpenAICompatibleProvider(BaseProvider):
    """Thin OpenAI-compatible chat completion client using HTTP (no vendor SDK required)."""
    def __init__(self, name, base_url, model, api_key_env):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key_env = api_key_env

    def reason(self, payload: dict) -> dict:
        import requests
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"missing {self.api_key_env} for provider '{self.name}'")
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": json.dumps(payload)}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        r = requests.post(f"{self.base_url}/chat/completions",
                          headers={"Authorization": f"Bearer {api_key}",
                                   "Content-Type": "application/json"},
                          json=body, timeout=120)
        r.raise_for_status()
        try:
            content = r.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, ValueError, IndexError) as e:
            logger.warning("empty/invalid JSON content from %s: %s", self.name, e)
            return {}   # caller's retry/fallback handles empty JSON (spec)


class DeepSeekProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            name="deepseek",
            base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),  # OpenAI-compatible (spec)
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-reasoner"),
            api_key_env="DEEPSEEK_API_KEY",
        )


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(name="openai", base_url="https://api.openai.com/v1",
                         model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                         api_key_env="OPENAI_API_KEY")


class LocalProvider(BaseProvider):
    """Local/private model (e.g. Ollama) — used when PHI cannot leave the environment.
    Default uses Qwen3-8B-Instruct (native tool-calling + JSON) for the reasoning cortex;
    pass model='biomistral:7b' for medical-domain grounding. NOTE: encoder models
    (GatorTron/ClinicalBERT) are NOT generators — use the embedding lane for those."""
    name = "local"
    def __init__(self, base_url="http://127.0.0.1:11434", model="qwen3:8b"):
        self.base_url = base_url.rstrip("/"); self.model = model
    def reason(self, payload: dict) -> dict:
        import requests
        r = requests.post(f"{self.base_url}/api/generate",
                          json={"model": self.model, "prompt": json.dumps(payload), "stream": False},
                          timeout=120)
        r.raise_for_status()
        return {"text": r.json().get("response", ""), "raw": True}


class _LocalEncoderProvider(BaseProvider):
    """Encoder lane (Clinical ModernBERT / nomic-embed-text / GatorTron-NER). Produces
    embeddings/entities, NOT generative reasoning. Placeholder — wire a real client on use."""
    name = "local-encoder"
    def __init__(self, model="nomic-embed-text"):
        self.model = model
    def reason(self, payload: dict) -> dict:
        raise NotImplementedError(
            "encoder lane is not a generator; call the embedding/ner service for this task")


def build_provider(name: str):
    if name == "deepseek":
        return DeepSeekProvider()
    if name == "openai":
        return OpenAIProvider()
    if name == "local-encoder":
        return _LocalEncoderProvider()
    if name.startswith("local"):
        return LocalProvider()
    return StubProvider(output={"error": f"unknown provider '{name}'"})
