# DOXIMITY RECONNAISSANCE — BEYOND THE OFFICIAL ORG (2026-08-05, founder-supplied + analysis)

**The third-party surface: the API-reconstruction, the auth-clients, the Ask-community workflow, the org-activity signals, the Tarka deep-dive. All = reconnaissance material, NOT authoritative specs.**

## 1. The API Evangelist reconstruction
- A third-party (unaffiliated) repo reconstructing Doximity's public OAuth/OIDC surface from public materials: apis.yml · the OAuth-OpenAPI-YAML · the OIDC-OpenAPI-YAML · the original artifacts · the auth-artifacts · the OAuth-scopes · the data-model · the error-defs · the rate-limits · the agentic/LLM/MCP-artifacts · the conformance info.
- THE VALUE: the endpoints/scopes/rate-limit patterns for the physician-identity lane — the recon, never the production-authority.

## 2. The third-party auth clients (the historical signals)
- Node-Passport-strategy (client-id/secret/redirect/access/refresh/profile for Express!) · the Push-Health-OmniAuth · the older-OmniAuth ×2 · the minimal-OmniAuth · DoxAuth · the historical-.NET-client — OLD code: inspect for the historical architecture (the endpoint-structures, the callback-shapes, the profile-responses), never for the modern-security patterns.

## 3. The Doximity-Ask community project
- An MIT-licensed JavaScript project: the 3-phase insurance-eligibility + patient-cost-estimation workflow using Doximity Ask (associated with an Op-Med article!) — THE NURA-value: the prior-auth/eligibility-workflow reference (the Weno + the Availity-lane parallel!).

## 4. The high-value official surfaces
- All-repos · ALL-PUBLIC-PRs (the change-history signals!) · all-issues · the recently-updated · the GitHub-packages · the org-activity — the searches: auth.doximity.com · profile:read · openid · doximity:// (the URL-scheme!) · OpenAPI/Swagger/GraphQL/webhook · Anthropic/Vertex-AI/LangChain (the AI-signals!) · Prometheus/NATS/Neo4j/Elasticsearch/Sidekiq.

## 5. The Tarka deep-dive (the cloned repo — the study-list)
- The docs-hub · the architecture · the investigation-pipeline · the diagnostic-modules · the playbook-system · the memory-system · the chat-architecture · the actions · the multi-provider-LLM-config · the examples · the Python/frontend-deps · the Docker-Compose · the GitHub-Actions — the NURA incident-commander reference (the clone: /opt/data/nura-clinical-ai/doximity/tarka!).

## 6. The NURA conclusions
- The API-recon + the OAuth-patterns + the Ask-workflow + the Tarka-docs = the meaningful additional material — the patterns-in, the proprietary-out.
- The physician-identity lane (the Sign-in-with-Doximity-compatible + the NPI-verification!) + the eligibility-workflow (the Ask-pattern!) + the incident-agent (the Tarka!) = the three takeaways.
