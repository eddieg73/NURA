# Orthanc → Wasabi S3 archive — activation recipe (keys pending)

## 1. Founder task (in Notion Owner Tasks)
Open a **Wasabi** account → create bucket (e.g. `nura-pacs-archive`) → drop to Hermes: access key + secret + bucket name (+ region, default us-east-1).

## 2. Activate (once keys are sealed)
Add to the orthanc compose env (Clinic /root/docker/orthanc/docker-compose.yml):
```yaml
      AWS_ACCESS_KEY_ID: "<sealed>"
      AWS_SECRET_ACCESS_KEY: "<sealed>"
      ORTHANC__AWS_S3_STORAGE__ENABLE: "true"
      ORTHANC__AWS_S3_STORAGE__BUCKET_NAME: "nura-pacs-archive"
      ORTHANC__AWS_S3_STORAGE__ENDPOINT: "https://s3.wasabisys.com"
      ORTHANC__AWS_S3_STORAGE__STORAGE_CLASS: "STANDARD"
```
Then `docker compose up -d` + verify: `GET /system` shows the S3 storage area active; a test study written to disk also appears in the bucket.

## 3. Tiering policy (configure in Orthanc after activation)
- Hot window: studies < 90 days stay on the Clinic disk (compressed).
- Archive: ≥ 90 days → S3 storage area (Orthanc handles transparently on access).
- Retention: MQSA mammo = 5 yr min / 10 yr standard — set the Orthanc storage scheduler accordingly; never auto-delete without the retention clock.

## 4. Fallback note
If Wasabi creds are delayed and the disk crosses 90%: temporary `docker system prune` + move the DB volume to a Hostinger-attached disk is the escape hatch. Wasabi is the real fix.
