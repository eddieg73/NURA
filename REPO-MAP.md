# NURA — the monorepo (the one-repo, all-projects!)

## The layout
```
NURA/
├── apps/
│   ├── nura_medical/        # the Flutter mobile app (Android+iOS!)
│   └── (future apps!)
├── backend/
│   ├── docsgpt/             # the DocsGPT-brain deployment!
│   └── (the API-services!)
├── automation/
│   └── n8n/                 # the workflow-exports!
├── infra/
│   ├── fleet/               # the server-configs + the WireGuard!
│   └── scripts/             # the ops-scripts (the managers · the guardians!)
├── docs/
│   └── (the architecture + the guides!)
└── README.md                # the map!
```

## The current-state
- `apps/nura_medical/` ← the app-code (the committed master!)
- The other projects (the docs-vault · the hermes-ecosystem · the scripts!) live locally — the monorepo holds the CODE-projects, the vault stays in Obsidian!

## The rules
- ONE repo (eddieg73/NURA!) — the projects as the directories!
- The secrets NEVER commit (the .gitignore ✓!)
- The CI per-app (the codemagic.yaml in the apps/nura_medical!)
