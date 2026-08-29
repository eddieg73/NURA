# LOM ON-DEVICE INFERENCE — LITERT-LM BRIDGE SPEC (2026-08-06)

**The LOM (Local On-device Model) doctrine meets the official Google engine: LiteRT-LM + Gemma3-1B-IT on the phone/glasses/truck — offline-first, GPU/NPU-accelerated, tool-capable. The nura-medical app's local brain.**

## 1. THE ENGINE (the Kotlin core)
- dependency: `com.google.ai.edge.litertlm:litertlm-android` (the Android!) / `litertlm-jvm` (the JVM!)
- EngineConfig: modelPath (the bundled .litertlm!) · backend = Backend.NPU (the nativeLibraryDir!) or GPU/CPU-fallback!
- engine.initialize() on a background coroutine (the 10s-load — never the UI thread!)
- The model: gemma3-1b-it-int4.litertlm (the generic universal — the ~1GB!) — the device-specific variants for the Snapdragon (sm8550/8650/8750/8850!) · MediaTek (mt6989/6991/6993!) · Tensor-G5 (the Pixel!) — the per-device optimization lane!

## 2. THE CONVERSATION (the LOM modes)
- ConversationConfig: systemInstruction (the LOM's clinical-scoring prompts!) · samplerConfig (topK/topP/temp — the deterministic scoring = low-temp!)
- sendMessageAsync (the streaming — the clinical outputs streamed live!)
- The LOM modes: (a) the SCORING (the NEWS2/RSBI/ARDSNet prompt-templates → the scores with the device-settings outputs!) (b) the CHAT (the patient-facing plain-language!) (c) the FIELD (the austere-med references!)
- extraContext: the Jinja-vars (the patient-vitals in, the scores out!)

## 3. THE TOOLS-USE (the on-device agentic)
- The model emits the tool-calls → the app executes the LOCAL device functions (the sensors · the settings · the OBD/truck-lane!) → the tool-responses → the final answer!
- The guardrails: the device-tools = the read-only + the operator-gated (the LOM's auto-SAFE defaults = the crashing/non-compliant only!)

## 4. THE FLUTTER BRIDGE (the nura-medical integration)
- Flutter → MethodChannel ("nura/lom") → the Kotlin engine-wrapper:
  - `loadModel()` → EngineConfig + initialize (the progress-streamed!)
  - `send(mode, prompt, vitals)` → ConversationConfig + sendMessageAsync → the streamed-response!
  - `getStatus()` → the backend (NPU/GPU/CPU) + the load-state!
- The offline-first: the LOM = the primary lane; the cloud (the DocsGPT/LiteLLM!) = the fallback when the connectivity's there!

## 5. THE SAFETY (the LOM doctrine unchanged)
- The ALWAYS-score (the NEWS2/RSBI/ARDSNet!) · the provider-gated consequential actions · the black-box-log + the MD-alert on the device-events · the defib-manual!
- The model-versioning: the .litertlm pinned per-release (the re-audit per the mechanistic-interpretation skill before the clinical use!)

## 6. THE VERIFICATION
- The engine-loads the model (the device-test: the Gemma3 answers locally!)
- The scoring-mode: the vitals-in → the NEWS2-out (the offline, no-network!)
- The tools-lane: the read-only device-call round-trip!
