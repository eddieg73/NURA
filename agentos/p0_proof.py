#!/usr/bin/env python3
"""P0 proof: drive the CoreCoder agent through the SOVEREIGN dock Ollama line.

No paid API, no Anthropic. Points OPENAI_BASE_URL at our dock Ollama (OpenAI-compat :11435).
Runs one real agent turn that must (a) call a tool, (b) get a tool result, (c) produce a reply.
"""
import os, sys, asyncio
sys.path.insert(0, "/opt/data/agentos-core")

# Point at the SOVEREIGN dock model (free, no credits) — OpenAI-compatible
os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:11435/v1"
os.environ["OPENAI_API_KEY"] = "ollama"      # any non-empty; Ollama ignores it
os.environ["CORECODER_MODEL"] = "qwen2.5:3b"
os.environ["CORECODER_PROVIDER"] = "openai"  # OpenAI-compat against Ollama

from corecoder import Agent
from corecoder.llm import LLM
from corecoder.tools import ALL_TOOLS

print(f"model: {os.environ['CORECODER_MODEL']} via {os.environ['OPENAI_BASE_URL']}")
# LLM(model, api_key, base_url) — no from_env. Point at sovereign dock Ollama.
llm = LLM(model=os.environ["CORECODER_MODEL"],
          api_key="ollama",                      # any non-empty; Ollama ignores
          base_url=os.environ["OPENAI_BASE_URL"])
agent = Agent(llm=llm, tools=ALL_TOOLS, max_rounds=4)
print(f"agent ready: {len(ALL_TOOLS)} tools loaded")

# One real agent turn — must call a tool (bash) and return a text reply
reply = agent.chat("Run the command `echo NURA_AGENT_OS_OK` using your bash tool, then tell me the exact output.")
print("\n=== AGENT REPLY ===")
print(str(reply)[:400])
