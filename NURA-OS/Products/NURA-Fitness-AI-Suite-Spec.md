# NURA Fitness AI — 12-Persona Program-Generator Suite (founder directive 2026-08-15)

**Product:** an AI fitness program generator that speaks in 12 expert personas — Equinox master trainer, NASM corrective specialist, Jeff Nippard hypertrophy scientist, CrossFit L3, Athlean-X bodyweight coach, Nike Run Club marathon coach, Renaissance Periodization recomp strategist, Peloton recovery specialist, Precision Nutrition fat-loss coach, Yoga-with-Adriene mobility instructor, Garmin data analyst, and the Equinox 90-day transformation integrator.

**Directive:** Atlas builds it; Paperclip team hired to execute.

## The 12 personas (prompt canon)

1. **Equinox Master Trainer** — personalized 12-week program: goal assessment, frequency, split design, exercise selection (sets/reps/rest/tempo), progressive overload, warm-up, cooldown/mobility, cardio integration, deload, 3-phase periodization (foundation→building→peak).
2. **NASM Corrective Exercise Specialist** — dysfunction screening, upper/lower assessments, core check, L/R imbalance, corrective Rx, foam rolling, movement prep, exercise modifications, 4-week reassessment.
3. **Jeff Nippard Hypertrophy** — 10-20 hard sets/muscle/week, 2-3x frequency, rep-range periodization, per-head exercise selection, intensity techniques, RIR system, mind-muscle cues, overload tracking, nutrition targets.
4. **CrossFit L3** — movement-pattern coverage, metcons, strength foundation, gymnastics, WOD structure, scaling, skill progression, mobility, benchmarks (Fran/Murph/1RM), recovery.
5. **Athlean-X Zero Equipment** — 30+ bodyweight library with progressions, full-body 3-day + 5-day split, intensity techniques (eccentrics/isometrics/1.5s), HIIT, core specialization, $50-100 equipment upgrades, milestones.
6. **Nike Run Club Marathon** — fitness assessment, goal race, weekly structure, pace zones, 10% mileage rule, long-run progression, speed work, injury prevention, race week, runner strength.
7. **Renaissance Periodization Recomp** — eligibility, calorie target, 1g/lb protein, training stimulus, nutrient timing, non-scale metrics, 4-week phases, sleep, stress, 3-6 month timeline.
8. **Peloton Recovery** — active recovery sessions, 15-min stretch, foam rolling, sleep optimization, recovery nutrition, DOMS vs injury, stress link, tracking metrics, deload, tool assessment (what works vs gimmicks).
9. **Precision Nutrition Fat Loss** — body-fat estimation, 300-500 cal deficit, protein fortress, hunger management, plateau protocol, diet breaks, cardio-as-later-tool, 8-12k steps, alcohol impact, month-by-month timeline.
10. **Yoga with Adriene Mobility** — tight-area assessment, daily 15-min routine, pre/post-workout mobility, hip/shoulder/ankle/spine protocols, 30-day progression benchmarks, maintenance.
11. **Garmin Tracking System** — workout log template, overload tracker, measurement protocol, photos, strength benchmarks, nutrition compliance score, sleep/recovery log, weekly review, monthly assessment, 90-day tracker.
12. **Equinox 90-Day Transformation** — 3 phases (foundation/build/peak), phased training + nutrition + cardio + recovery, weekly milestones, accountability system, day-91 maintenance plan.

## Build notes
- Each persona = a prompt module with a `[PROFILE]` intake block (age/gender/experience/equipment/days/goal).
- Delivery: web UI (persona picker + intake form → generated program) — fits the Paperclip stack.
- Safety: standard fitness disclaimers; no medical claims; NASM/persona brands are stylistic framing only.
- Team: Atlas (CEO, assume-control) + product + prompt-engineer + QA + marketing.
