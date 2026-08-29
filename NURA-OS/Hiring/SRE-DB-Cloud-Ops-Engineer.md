# SITE RELIABILITY, DATABASE & CLOUD OPERATIONS ENGINEER — the role spec (2026-08-04)

**Position:** Site Reliability, Database & Cloud Operations Engineer · **Funnel:** the AI hiring manager · **Signer:** the founder

## 1. MISSION
Keep NURA's production estate running: the 3-node fleet (Clinic 72.61.71.211 · Lab 72.60.163.140 · Edge 195.35.32.113), the Docker/K8s workloads, PostgreSQL/Redis/Qdrant, the n8n/gateway lanes, and the cloud (AWS/RunPod-class) — with SLAs/SLOs, capacity planning, observability, incident response, backup/DR discipline (tested restores only), and release reliability. **The doctrine: availability is a patient-safety property.**

## 2. CORE OWNERSHIP
**SRE:** uptime + SLIs/SLOs · capacity planning · error budgets · incident response (the incident-commander doctrine) · release reliability (staging mirrors production, automated rollback) · chaos/resilience tests · performance tuning.
**Databases:** PostgreSQL (replication, partitioning, backups/PITR, tuning, the OpenEMR + Perfex + Hermes DBs) · Redis (the ONE memory Redis = Clinic redis-gc8b, cache/queue discipline) · Qdrant (the nura-os vector collection, index health) · data lifecycle.
**Cloud ops:** AWS where used · RunPod governance · object storage (S3 lanes) · Terraform/IaC · the Hostinger fleet lifecycle (snapshots, migrations, the 3-node placement doctrine) · certificate/DNS operations (the NPM/Traefik map).

## 3. REQUIRED STACK & EXPERIENCE
Linux · Docker · Kubernetes/Helm · Terraform/Ansible · PostgreSQL + Redis + Qdrant administration · Prometheus/Grafana/Loki · OpenTelemetry · n8n/gateway operations · incident tooling (PagerDuty-class) · cloud (AWS) · Bash/Python/Go.
**Experience:** 5+ yrs SRE/ops · 3+ yrs production PostgreSQL · container orchestration · observability at scale · regulated/healthcare environments (preferred) · on-call discipline · the ability to run a clean postmortem (blameless, evidence-first).

## 4. RECOMMENDED CERTIFICATIONS
CKA · AWS SA · Google PCA · Red Hat · PostgreSQL Professional (or equivalent) · ITIL · CKAD. Certs ≠ ability — the exam decides.

## 5. THE PRACTICAL EXAM (the gate)
Given a production incident (a DB outage + a gateway failure + a queue backlog), deliver: the SLO impact assessment, the runbook (containment → restore → verify → postmortem), the actual restore from a backup (proven, not described), the capacity projection, and the monitoring deltas that would have caught it earlier — including the dashboard queries and the alert thresholds.

## 6. FIRST 90-DAY DELIVERABLES
**1-30:** the fleet baseline (resources, backups, certificates, drift) · the SLO/SLI definitions · the monitoring gaps → the alerting baseline · the backup-restore PROOF (all critical systems tested).
**31-60:** the incident runbooks (DB/gateway/lane/disk) · the chaos tests (kill Redis, kill the queue, disk-full) · the capacity plan · the n8n/gateway reliability pass.
**61-90:** the DR exercise (full restore) · the error budgets live · the on-call rotation + the postmortem process · the executive reliability report (honest numbers).

## 7. KPIs
Availability vs SLO · error budget burn · MTTD/MTTR · backup success + restore success (tested) · capacity headroom · patch cadence · incident count/severity · on-call load. **Targets: critical systems ≥99.9% · restore-tested ≥ monthly · silent failures = 0 · unmonitored critical paths = 0.**

## 8. THE JD SUMMARY
The SRE/DB/Cloud Ops Engineer is the guardian of "it stays up": the databases answer, the fleet breathes, the lanes route, and every restore is proven before it's needed. The role requires deep ops craft, database mastery, cloud discipline, and the calm of an incident commander under pressure.
