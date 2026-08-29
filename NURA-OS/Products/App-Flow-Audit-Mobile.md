# App Flow Audit — NURA Mobile (Flutter)

**Date:** 2026-08-19
**Scope:** `/opt/data/nura_medical/apps/nura_medical` — `lib/main.dart` + 5 screens (Scribe · Clinical · Ops · E6B · Account)
**Constraints honored:** Read-only audit. No code changed, no breaking changes.
**Toolchain:** Flutter 3.47.0 stable · Dart 3.13.0 · platforms: android, ios, macos, web, windows (no linux)

---

## 1. Static verification

| Check | Result |
|---|---|
| `flutter analyze` | ✅ **No issues found!** (15.6s) — verified still clean |
| `flutter test` | ❌ **FAILS** — `test/widget_test.dart` is the stale default "Counter increments smoke test"; it expects a counter app that no longer exists (`line 19`). Tests are broken even though the app compiles clean. |
| Imports | ✅ All screens import only `material`, `dart:convert`, `dart:io`, `dart:math` — all resolve. No broken imports. |
| `pubspec.yaml` | ⚠️ Description is still the Flutter default *"A new Flutter project"*; no `http` package (uses `dart:io HttpClient` — see web gap below). |

---

## 2. Per-screen status

### main.dart — ✅ OK
- 5-tab shell wired correctly: `NavigationBar` (Scribe · Clinical · Ops · E6B · Account) + `IndexedStack`, all destinations map to the right screens, `setState` tab switching, state preserved across tabs.
- Icons/labels match their tabs. No dead code.
- ⚠️ UI: the outer `Scaffold` has an `AppBar` ("NURA — the ONE app") **and every child screen has its own `AppBar`** → double stacked app bars on every tab.

### Scribe (scribe_screen.dart) — ❌ ISSUE (functional break)
- ❌ **Endpoint is a placeholder:** `kScribeApi = 'http://YOUR_GATEWAY:8095/scribe'` — the primary button always fails ("host not found"). Comment says "override per deployment" but it's a `const`, so it can't be overridden at runtime. Should be `http://127.0.0.1:8095/scribe` to match the Clinical tab.
- ❌ Mic icon implies voice dictation; there is no speech-to-text — text-only input. Icon misleads.
- ⚠️ `jsonDecode(body)['note']` assumes the response is a JSON map with a `note` key; malformed responses surface as raw error strings.
- ⚠️ `HttpClient` never closed; no timeout (a hung engine = stuck spinner forever).
- ✅ Empty-input guard, busy state, error display, [review]-flag placeholder copy all present.

### Clinical (clinical_screen.dart) — ✅ OK (endpoints correct) + ⚠️ latent bug
- ✅ **Endpoints verified correct:** `http://127.0.0.1:8095/dx`, `/synthesis`, `/scribe` — built via `postUrl(Uri.parse('http://127.0.0.1:8095/$tool'))`, all three buttons (DX / SYNTHESIS / SCRIBE) wired, disabled while busy. POST JSON `{'text': ...}`. DRAFT + PROVIDER-APPROVAL label appended.
- ⚠️ **Latent crash:** `e.toString().substring(0, 80)` in the catch block throws `RangeError` when the error message is shorter than 80 chars (e.g., a short engine error) — the catch handler itself can crash the app.
- ⚠️ No timeout on `HttpClient`; `client.close()` only on the success path (leak on error).
- ⚠️ `_caseText` controller never disposed.

### Ops (ops_screen.dart) — ❌ ISSUE (all buttons dead)
- ❌ All 6 tiles (Patient Texts, Payments, Fax, Reviews, Reminders, Akaunting Books) are static `ListTile`s with **no `onTap`** — the entire tab is a mock. Every lane is marked "pending" (Twilio, NMI, Documo, Google, n8n, Akaunting).
- ⚠️ No status indicators (connected/pending), no empty states, no navigation targets.

### E6B (e6b_screen.dart) — ✅ OK (functional) + ⚠️ edge cases
- ✅ Fully local math — TAS/wind/course/distance/burn → GS · HDG · ETE · Fuel. CALCULATE wired, results render, pilot-use disclaimer present.
- ⚠️ **NaN risk:** if TAS = 0, `crosswind / tas` → Infinity/NaN and the screen prints "GS NaN kt · HDG NaN°". GS has a div-by-zero guard; TAS does not.
- ⚠️ WCA formula (`crosswind/tas · 60/π`) is a small-angle approximation — fine for a planning aid, worth a footnote.
- ⚠️ Body is a non-scrollable `Column` — overflows on small phones with the keyboard up. Controllers never disposed.

### Account (account_screen.dart) — ❌ ISSUE (all cards dead, gate unimplemented)
- ❌ The license gate (NPI/paramedic) is **description-only** — no input, no verification, no gating of clinical features. The founder's law is not enforced anywhere.
- ❌ All 3 cards (license gate, provider profile, settings) are static — no `onTap`.
- ⚠️ No logout, no app version, no endpoint/gateway configuration UI.

---

## 3. Flow gaps (what's missing for a smooth user journey)

1. **Scribe tab is a dead end** — placeholder `YOUR_GATEWAY` endpoint fails every time; the user must go to the Clinical tab to get a working scribe. The two scribe paths must share one configured gateway.
2. **No gateway configuration surface** — `127.0.0.1:8095` is hardcoded everywhere (and `YOUR_GATEWAY` in Scribe). There is no settings field to point the app at a real deployment, and loopback breaks on physical phones (Android emulator needs `10.0.2.2`). The Settings card exists as a mock but does nothing.
3. **Ops is a menu with no rooms behind the doors** — six practice lanes, zero actions. Even "coming soon" tiles need taps that give feedback (snackbar/roadmap), not silent dead tiles.
4. **The license gate doesn't gate** — clinical features are reachable without any verified credential. No first-run onboarding: open app → verify NPI → unlock.
5. **No loading/error design language** — the Clinical and Scribe tabs each invent their own busy/error treatment (text dump vs. red label). No skeletons, no retry button, no offline banner.
6. **Web target is broken in practice** — `dart:io` (used by Scribe + Clinical) does not compile on web, and the `web/` platform dir is present, so `flutter build web` will fail. Either drop web or move HTTP to a cross-platform client (`package:http`).
7. **Tests are stale and failing** — `widget_test.dart` still tests the default counter. Zero coverage of the 5 tabs, endpoint paths, or E6B math. CI would be red on day one.
8. **No navigation beyond the tab bar** — no detail routes exist; every future feature (texts, payments, fax) has nowhere to push to.

## 4. UI-polish list (Doximity-grade recommendations)

- **Fix the double AppBar** — one app bar (title per tab), or move the brand to the Account tab. Two stacked bars is the first thing every user sees.
- **Design the DRAFT label as a visual badge** — amber `Chip`/banner with a lock icon on result cards, not appended plain text. Provider-review affordance should be unmissable and consistent across Scribe/Clinical.
- **Result panels** — monospace/serif output area, copy-to-clipboard action, auto-scroll to latest, "Retry" button on error states (Clinical currently has none).
- **Ops tiles** — actionable cards with leading status dots (green = live, amber = pending), chevrons, and per-lane subtitles that state *what happens when it's live*. Add `onTap` → "Lane pending — wired next sprint" feedback so nothing feels broken.
- **Scribe** — swap the mic icon for `keyboard_voice` until real STT exists (or add STT), add patient/demographic context fields (age/sex/visit type) like real ambient scribes.
- **E6B** — wrap in a scroll view, put results in a Card with big numbers, add a Reset button, guard TAS = 0 with an inline validation message.
- **Account** — real license-gate form (NPI + license # with format validation), app version row, audit-log stub, gateway URL field (kills flow gap #2).
- **Global** — dark theme (clinicians at night), consistent typography scale (currently 11/13px ad hoc), branded seed color already good (`#0B3D91`), empty-state illustrations instead of grey sentences.
- **pubspec/hygiene** — real description, replace stale `widget_test.dart` with a 5-tab smoke test (render each tab, tap CALCULATE, assert endpoint strings), optionally `flutter_lints` severity review.

---

## 5. Summary

The app compiles clean (`flutter analyze`: no issues) and the five-tab shell is correctly wired with sound imports, but only two of the six surfaces are genuinely functional — the Clinical tab (with its verified `127.0.0.1:8095/dx|/synthesis|/scribe` endpoints and DRAFT labeling) and the local E6B math — while the Scribe tab points at an unresolvable `YOUR_GATEWAY` placeholder, the Ops tab is six dead tiles, and the Account tab's license gate is description-only, so roughly half the app's visible controls do nothing; underneath, the test suite is a stale failing counter test, the web target is silently broken by `dart:io`, and a latent `substring(0,80)` RangeError can crash the Clinical error handler on short messages. The highest-leverage fixes, in order: point Scribe at the real gateway, add a gateway/License-gate configuration surface, give Ops/Account tiles real taps and status, fix the double AppBar and the DRAFT badge styling, and replace the widget test with a real smoke test — all achievable without touching the working Clinical and E6B logic.
