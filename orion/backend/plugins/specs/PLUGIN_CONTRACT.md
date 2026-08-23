# ORION Plug-in Contract v1.0

Every plug-in must implement the following:
1. **Discovery:** `describe()`: Returns capabilities and expected JSON schema.
2. **Execution:** `execute(params)`: Performs action and returns structured output.
3. **Health:** `status()`: Returns health and version.
4. **Audit:** All output must be piped to the /audit lane before reaching the UI.
