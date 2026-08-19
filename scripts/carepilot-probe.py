import re, http.cookiejar, urllib.request, urllib.error, ssl

BASE = "https://carepilot.nuratech.ai"
USER, PWD = "Alexsis", "Alexsis"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)")]

def get(path):
    try:
        with opener.open(BASE + path, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "ignore"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore"), dict(e.headers)
    except Exception as e:
        return 0, str(e), {}

# 1) login page + CSRF
st, body, hdrs = get("/login")
tok = re.search(r'name="_token" value="([^"]+)"', body)
print("login page:", st, "| csrf:", bool(tok), "| cookies:", [c.name for c in cj])
if not tok:
    print("no csrf — abort"); raise SystemExit(1)

# 2) POST login
data = urllib.parse.urlencode({"_token": tok.group(1), "username": USER, "password": PWD}).encode()
req = urllib.request.Request(BASE + "/login", data=data, method="POST")
req.add_header("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
req.add_header("Referer", BASE + "/login")
try:
    with opener.open(req, timeout=25) as r:
        final = r.geturl()
        st2 = r.status
        dash = r.read().decode("utf-8", "ignore")
except urllib.error.HTTPError as e:
    st2, final, dash = e.code, e.geturl() if e.geturl() else BASE + "/login", e.read().decode("utf-8", "ignore")
print("POST /login ->", st2, "| landed:", final[:80])

# 3) probe dashboard + discover links/modules
st3, dash, _ = get(final.replace(BASE, ""))
title = re.search(r"<title>(.*?)</title>", dash, re.S)
links = sorted(set(re.findall(r'href="(/[^"#?]*)"', dash)))
print("title:", title.group(1).strip() if title else "none", "| links:", len(links))
for l in links[:40]:
    print("  ", l)
