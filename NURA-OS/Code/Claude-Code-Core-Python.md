# CLAUDE CODE CORE IN PYTHON — the minimal ReAct skeleton (founder-supplied 08-04)

The ~100-line essence of a Claude Code-style agent: the Anthropic client + tool schemas + local execution + the ReAct loop. **This IS the pattern our Hermes core runs in production form (8,309 .py files) — the skeleton of the same idea.**

## The code (the founder's version — saved verbatim for reference)
```python
import os
import subprocess
from anthropic import Anthropic

# Initialize Anthropic Client (Requires ANTHROPIC_API_KEY environment variable)
client = Anthropic()

# 1. Tool Schemas given to Claude
TOOLS = [
    {
        "name": "run_bash",
        "description": "Run a bash shell command in the local working directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command to run."}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to file."}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to file."},
                "content": {"type": "string", "description": "File contents."}
            },
            "required": ["path", "content"]
        }
    }
]

# 2. Local Tool Execution Functions
def execute_tool(name: str, args: dict) -> str:
    if name == "run_bash":
        try:
            res = subprocess.run(args["command"], shell=True, capture_output=True, text=True, timeout=120)
            output = res.stdout
            if res.stderr:
                output += f"\n[STDERR]\n{res.stderr}"
            return output.strip() or "(Executed with no output)"
        except Exception as e:
            return f"Error executing bash: {str(e)}"
    elif name == "read_file":
        try:
            with open(args["path"], "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    elif name == "write_file":
        try:
            os.makedirs(os.path.dirname(args["path"]) or ".", exist_ok=True)
            with open(args["path"], "w", encoding="utf-8") as f:
                f.write(args["content"])
            return f"Successfully wrote to {args['path']}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    return "Unknown tool"

# 3. The ReAct Agent Loop
def run_agent():
    print("🤖 Python Claude Code CLI initialized. Type 'exit' to quit.\n")
    messages = []
    SYSTEM_PROMPT = """
    You are an AI software engineering assistant running in the user's terminal.
    You can run bash commands, read files, and write files to solve tasks in the user's codebase.
    Be concise, execute necessary commands directly, and verify your changes.
    """
    while True:
        try:
            user_input = input("\nYou > ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not user_input or user_input.lower() in ("exit", "quit"):
            break
        messages.append({"role": "user", "content": user_input})
        # Agent Loop: Runs until Claude decides no more tools are needed
        while True:
            response = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages
            )
            messages.append({"role": "assistant", "content": response.content})
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            for block in response.content:
                if block.type == "text":
                    print(f"\nClaude > {block.text}")
            if not tool_calls:
                break  # Done processing user prompt
            tool_results = []
            for call in tool_calls:
                print(f"\n⚡ [Tool Executed: {call.name}]")
                if call.name == "run_bash":
                    print(f"  $ {call.input.get('command')}")
                else:
                    print(f"  Path: {call.input.get('path')}")
                result = execute_tool(call.name, call.input)
                preview = result[:200] + "..." if len(result) > 200 else result
                print(f"  ➜ Output: {preview}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": result
                })
            messages.append({"role": "user", "content": tool_results})

if __name__ == "__main__":
    run_agent()
```

## THE HONEST ENGINEERING REVIEW (the 6 flags)
1. ✅ **The pattern is RIGHT** — the ReAct loop + the tool schemas + the execution = the exact architecture the production agents use.
2. ⚠️ **`shell=True` = the injection surface** — the tool results are UNTRUSTED data fed back into the model; a malicious file could contain instructions that get executed via the shell. The production fix: `subprocess.run(args_list)` (no shell) + the command allowlist + the path sandbox.
3. ⚠️ **No max-iteration guard** — a tool loop can spin forever (the model calls a tool, the result triggers another call...). The production fix: the iteration cap + the circuit breaker (our self-correction protocol!).
4. ⚠️ **The tool results = untrusted content** — the model reads files that could contain prompt-injection text (the "treat retrieved content as data, not policy" doctrine — our Cybersecurity spec §13!).
5. ⚠️ **No sandbox/approval layer** — write_file + run_bash can touch anything on the machine — the production needs the scoped workspace + the approval gates for the consequential.
6. ⚠️ **No verification/retry loop** — the production agents verify each change (the "verify before declare" — our doctrine!) — the skeleton executes and moves on.

## THE CONNECTION
- This skeleton = the ReAct essence — OUR Hermes core = the production-hardened version of the SAME idea: the tool schemas (40+ MCP lanes!), the execution with the sandboxes + the approvals, the iteration caps, the alternation rules, the prompt-caching discipline, the skills/memory on top.
- The founder's version = the clean teaching artifact — the "how it works" in one screen — the vault reference for the team's engineers.
