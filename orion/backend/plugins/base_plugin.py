import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PluginResponse(BaseModel):
    status: str = Field(..., description="success or error")
    data: Any = Field(..., description="The actual result of the execution")
    audit_id: str = Field(..., description="ID of the log entry in B2")

class OrionPlugin:
    """Base class for all ORION plug-ins.
    Plugins must be registered in /opt/data/nura_medical/orion/backend/plugins.
    """
    def __init__(self, config: Dict):
        self.config = config

    async def describe(self) -> Dict:
        raise NotImplementedError("Plugins must implement describe()")

    async def execute(self, params: Dict) -> PluginResponse:
        raise NotImplementedError("Plugins must implement execute()")

    async def status(self) -> Dict:
        return {"status": "online", "version": "1.0.0"}
