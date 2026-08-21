#!/usr/bin/env python3
"""NURA Aero swarm-sim — original Python swarm engine (EMS-first).
Formation choreography (Verge concept) + flocking + failsafe ladder (Anduril doctrine).
Clean implementation — reference architectures only, no copied code.
"""
import json, math, random, time

# ---------- mission file (the product: Verge-style choreography) ----------
MISSION = {
    "id": "EMS-001-medical-cross",
    "formation": "cross",          # grid | circle | cross
    "drones": 20,
    "altitude_m": 120,
    "spacing_m": 8.0,
    "speed_max_mps": 20.0,
    "geofence": {"center": [0, 0], "radius_m": 250.0},
    "payload": "aed_pod",
}

def formation_positions(n, kind, spacing):
    pts = []
    if kind == "grid":
        side = math.ceil(math.sqrt(n))
        for i in range(n):
            pts.append([(i % side) * spacing - side * spacing / 2, (i // side) * spacing - side * spacing / 2])
    elif kind == "circle":
        for i in range(n):
            a = 2 * math.pi * i / n
            pts.append([math.cos(a) * spacing * n / (2 * math.pi), math.sin(a) * spacing * n / (2 * math.pi)])
    elif kind == "cross":          # medical cross: 3 lines of the Red Cross
        arm = max(2, n // 4)
        # horizontal arm
        for i in range(-arm, arm + 1):
            pts.append([i * spacing, 0])
        # vertical arm (skip center dup)
        for i in range(-arm, arm + 1):
            if i != 0:
                pts.append([0, i * spacing])
        while len(pts) < n:        # pad to n
            pts.append([0, (len(pts) - n) * spacing])
        pts = pts[:n]
    return pts

class Drone:
    def __init__(self, idx, target):
        self.id = idx
        self.pos = [random.uniform(-120, 120), random.uniform(-120, 120)]
        self.target = target
        self.state = "forming"     # forming | holding | rtl | landed
        self.speed_max = MISSION["speed_max_mps"]
        self.vel = [0.0, 0.0]

    def step(self, dt, neighbors):
        tx = self.target[0] - self.pos[0]; ty = self.target[1] - self.pos[1]
        dist = math.hypot(tx, ty)
        if dist < 0.5:
            self.state = "holding"
            self.vel = [0.0, 0.0]
            return
        # --- seek target (dominant) ---
        vx = tx / dist * self.speed_max
        vy = ty / dist * self.speed_max
        # --- separation ONLY when far from own target (fixes collinear oscillation) ---
        if dist > 3.0:
            for o in neighbors:
                dx = self.pos[0] - o.pos[0]; dy = self.pos[1] - o.pos[1]
                d2 = dx * dx + dy * dy
                if 0 < d2 < 36:
                    f = 1.0 / max(d2, 0.5)
                    vx += dx * f * 0.4; vy += dy * f * 0.4
        vmag = math.hypot(vx, vy)
        if vmag > self.speed_max:
            vx *= self.speed_max / vmag; vy *= self.speed_max / vmag
        # --- velocity damping near target (convergence) ---
        damp = min(1.0, dist / 8.0)
        self.vel[0] = self.vel[0] * (1 - damp) + vx * damp
        self.vel[1] = self.vel[1] * (1 - damp) + vy * damp
        self.pos[0] += self.vel[0] * dt; self.pos[1] += self.vel[1] * dt

    # --- failsafe ladder (Anduril doctrine) ---
    def failsafe(self, mission):
        gx, gy = mission["geofence"]["center"]
        r = mission["geofence"]["radius_m"]
        if math.hypot(self.pos[0] - gx, self.pos[1] - gy) > r:
            self.state = "rtl"      # rung 2: return-to-launch (origin)
            self.target = [0, 0]
            return "geofence_breach"
        return None

def run(mission, steps=400, dt=0.1):
    targets = formation_positions(mission["drones"], mission["formation"], mission["spacing_m"])
    drones = [Drone(i, t) for i, t in enumerate(targets)]
    events = []
    for s in range(steps):
        # neighbor lookup (spatial hash would scale; O(n^2) fine for <500 in sim)
        for d in drones:
            if d.state in ("forming", "holding"):
                ev = d.failsafe(mission)
                if ev and ev not in events:
                    events.append(ev)
                if d.state == "rtl":
                    if math.hypot(d.pos[0], d.pos[1]) < 0.5:
                        d.state = "landed"
                    else:
                        dx = -d.pos[0]; dy = -d.pos[1]
                        m = math.hypot(dx, dy)
                        d.pos[0] += dx / m * d.speed_max * dt
                        d.pos[1] += dy / m * d.speed_max * dt
                    continue
            if d.state == "forming":
                d.step(dt, [o for o in drones if o is not d])
        # convergence check
        if s % 50 == 0:
            holding = sum(1 for d in drones if d.state == "holding")
            if holding == len(drones):
                return {"converged_step": s, "drones": len(drones), "state": "formation_hold", "events": events}
    return {"converged_step": None, "drones": len(drones), "state": "timeout", "events": events,
            "final_states": {d.id: d.state for d in drones}}

if __name__ == "__main__":
    print("=== NURA Aero swarm-sim: mission", MISSION["id"], "===")
    t0 = time.time()
    result = run(MISSION)
    print(json.dumps(result, indent=1))
    print(f"sim wall-time: {time.time() - t0:.2f}s")

    # geofence breach scenario (1 drone starts outside)
    print("\n=== failsafe test: 1 drone starting outside geofence ===")
    mission2 = dict(MISSION); mission2["geofence"]["radius_m"] = 100.0
    t = formation_positions(mission2["drones"], "cross", mission2["spacing_m"])
    d0 = Drone(0, t[0]); d0.pos = [500, 500]
    drones = [d0] + [Drone(i, t[i]) for i in range(1, len(t))]
    from collections import namedtuple
    print("drone 0 failsafe:", d0.failsafe(mission2), "-> state:", d0.state)
