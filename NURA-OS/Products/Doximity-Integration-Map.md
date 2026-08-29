# DOXIMITY INTEGRATION MAP — THE PROVIDER REFERENCES (2026-08-05, founder-supplied)

**The 6 surfaces: Django-allauth (the built-in provider!) · Laravel-Socialite (HIE-of-One) · Go (journalclub) · the API-Evangelist full artifacts · the api-search mirrors · the repository-history surfaces.**

## 1. The Django integration (the reference implementation)
- django-allauth's BUILT-IN Doximity provider: provider.py (the OAuth2 strategy + the profile-mapping!) · views.py (the OAuth-endpoints) · urls.py (the callbacks) · tests.py (the provider-tests!) · the .rst-docs — the most complete, tested reference (the callback-routes + the field-mapping!).

## 2. The Laravel/PHP provider
- shihjay2/hieofone-directory's SocialiteProviders/Doximity/src/Provider.php — the authorization-URLs, the token-URLs, the profile-retrieval + the returned-field-mapping.

## 3. The Go integration
- ripply/journalclub: src/config/oauth.go (the OAuth-config!) · src/config/doximity.go (the Doximity-module!) · ENV_VARS.md (the environment!) · src/accountsetup/accountsetup.go (the account-setup flow!).

## 4. The machine-readable artifacts (the cloned repo: api-evangelist-recon ✓)
- well-known/: openid-configuration.json · oauth-authorization-server.json · the well-known-catalog · the security.txt-reconstruction!
- authentication/ · scopes/ · openapi/ (the 2-refined + the _original!) · overlays/
- **mcp/doximity-mcp.yml · llms/doximity-llms.txt · skills/doximity-verify-member.md · skills/doximity-refresh-and-revoke.md** (the agent-artifacts — the verify-member + the refresh-revoke = the NURA-skill references!)
- data-model/ · errors/ · rate-limits/ · conventions/ · conformance/ · packages/ · lifecycle/

## 5. The api-search mirrors
- _scopes/doximity/doximity-scopes.md · _security/doximity/{authentication,trust-center,domain-security,vulnerability-disclosure}.md — the organized public summaries.

## 6. The history surfaces (the fork-network intel)
- For every official repo: commits · branches · tags · releases · network/members (the forks = the older implementations!) · closed-PRs · issues · actions · dependents — the closed-PRs + the commit-history = often more revealing than the README.

## The NURA take
- The Django-provider = the tested reference for OUR physician-identity provider (the Python-stack-fit! — the allauth-pattern → the Keycloak/OAuth-strategy!)
- The agent-artifacts (the verify-member + the refresh-revoke skills!) = the pattern for OUR agent-skills (the provider-verification + the token-lifecycle!)
- The MCP-definition + the LLM-profile = the agent-surface patterns.
