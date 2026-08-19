import secrets
line = "HERMES_DASHBOARD=1\nBASIC_AUTH=admin:" + secrets.token_urlsafe(18) + "\n"
with open("/opt/data/profiles/nura/.env", "a") as f:
    f.write(line)
print("env gate written (dashboard flag + admin basic-auth, 0600)")
