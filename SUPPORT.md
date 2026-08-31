# Support and Escalation

## General engineering questions

Use a GitHub issue for reproducible bugs, feature proposals, documentation defects, and non-sensitive operational work.

## Security

Do **not** publish credentials, tokens, private keys, PHI, vulnerability exploit details, or sensitive infrastructure data in a public issue. Follow `SECURITY.md` and use a private approved reporting channel.

## Clinical safety

Potential patient-safety defects are treated as high priority. Stop or disable the affected automated action when necessary to protect patients and evidence, preserve logs, and escalate through the approved clinical and engineering governance path.

## Production incidents

For production incidents:

1. protect patients, data and credentials;
2. stop unsafe automation without destroying evidence;
3. record the affected service/version and timeline;
4. restore the last known safe version when appropriate;
5. verify recovery end to end; and
6. document corrective action and a regression test.

GitHub issues are an engineering record, not a place to store PHI or production secrets.
