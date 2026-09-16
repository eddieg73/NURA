# AWS Server → Tailscale Join Runbook
**Target:** `carepilot.nuratech.ai` = **34.194.106.224** (AWS EC2, us-east-1)
**Prepared:** 2026-09-15 by Hermes (VPS)
**Status:** BLOCKED — 3 independent blockers, all needing founder/Oussama action

---

## What I verified (live, not assumed)

| check | result |
|---|---|
| Target identity | `34.194.106.224`, reverse DNS `ec2-34-194-106-224.compute-1.amazonaws.com` |
| What it serves | CarePilot Laravel — `Apache/2.4.68 (Debian)`, 302 → `/dashboard` |
| Ports | 80 OPEN, 443 OPEN, **22 SSH FILTERED**, 41641 closed, 8642 closed |
| Already on tailnet? | **NO** — 10 nodes in `eddie.secure@`, none is AWS |
| Fleet key SSH | **timed out** (security group blocks us) |
| AWS API creds in .env | **DEAD** — `STS InvalidClientTokenId`; values are `user_3…` / `rps_…` shaped, not `AKIA…` |
| Tailscale auth key held | `TS_AUTHKEY_WINDOWS` = 17 chars, does **not** start `tskey-auth-` ⇒ **unusable** |

---

## BLOCKER 1 — AWS security group blocks SSH
Nothing can be installed until the security group allows SSH from us.

**Our egress IPs (whatever you allowlist must match):**
```
clinic (and the Hermes container)   72.61.71.211
lab                                 72.60.163.140
edge                                195.35.32.113
```
Console path: **EC2 → the instance → Security → Security groups → Inbound rules → Add rule**
```
Type: SSH   Protocol: TCP   Port: 22   Source: 72.61.71.211/32
```
Do this for whichever host you want performing the install. If you'd rather not
open SSH at all, the alternative is **AWS Systems Manager (SSM) Session Manager** —
it needs no inbound rule, but the instance must have the SSM agent + an instance
profile with `AmazonSSMManagedInstanceCore`.

---

## BLOCKER 2 — no working AWS API credentials
The `AWS_*` values in `profiles/nura/.env` **are not AWS credentials**. A real AWS
access key ID is 20 characters beginning `AKIA`; this is 32 characters beginning
`user_3`, with a `rps_` secret, and STS rejects it. So I have no way to read the
account, list instances, or edit the security group myself.

**Needed:** a fresh IAM access key (or an instance profile) for an identity that
can at minimum describe EC2 and modify its security group. Seal it into
`profiles/nura/home/.secrets/aws.env` (mode 600) — do **not** paste it in chat.

---

## BLOCKER 3 — no valid Tailscale auth key
A join needs a key that looks like:
```
tskey-auth-kXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXX
```
Generate it at **login.tailscale.com → Settings → Keys → Generate auth key**
(recommended: **reusable**, **pre-approved**, expiry 90 days, tagged e.g. `tag:aws`).
The one in `.env` is 17 characters and cannot work.

---

## The command to run ON the AWS server (once 1–3 are resolved)

Amazon Linux / RHEL family:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey=tskey-auth-XXXXXXXXXX-XXXXXXXXXXXXXX \
  --hostname=aws-carepilot --accept-routes=false --ssh
```

Debian / Ubuntu:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey=tskey-auth-XXXXXXXXXX-XXXXXXXXXXXXXX \
  --hostname=aws-carepilot --accept-routes=false --ssh
```

Verify:
```bash
tailscale status
tailscale ip -4
```
Then from the clinic: `tailscale status | grep aws-carepilot`

---

## Once unblocked, I can do all of the following myself
1. Install Tailscale on `34.194.106.224` and join it to the tailnet
2. Add it to the **WireGuard mesh** on `10.10.0.0/24` as `10.10.0.4`
   (clinic .1 / lab .2 / edge .3 are already healthy; each node holds only its own key)
3. Publish it into the **Notion fleet inventory** as a fourth node, with its
   containers, ports, vhosts and certs
4. Wire **load balancing** across the mesh if you want it
5. Re-point `carepilot.nuratech.ai` DNS/naming decisions as part of migration

---

## One decision you should make before the migration goes further
**CarePilot's source is unreachable.** The live app is this AWS instance
(Apache/Laravel), but its source code exists on no host I can reach — the SoT at
`/root/.hermes/carepilot` is a *different* FastAPI app (`carepilot-api` on clinic:8100).
If Oussama is moving things to AWS, the Laravel source needs to come under version
control first, or the migration will move a binary nobody can rebuild.
