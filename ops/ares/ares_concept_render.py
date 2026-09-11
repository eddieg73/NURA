#!/usr/bin/env python3
"""NURA ARES — engineering concept render (what the device actually looks like).
Panels: base unit 3-view w/ dimensions | deployment on litter | fluidic circuit | SWaP mass budget.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrow, Polygon, Wedge
import numpy as np

BG, FG, ACC, ACC2, GRID = "#0d1117", "#e6edf3", "#ff8c42", "#58a6ff", "#30363d"

fig = plt.figure(figsize=(22, 15), facecolor=BG)
gs = fig.add_gridspec(2, 2, hspace=0.22, wspace=0.16,
                      left=0.045, right=0.972, top=0.905, bottom=0.055)

def style(ax, title, sub=None):
    ax.set_facecolor(BG)
    for s in ax.spines.values(): s.set_color(GRID)
    ax.tick_params(colors=FG, labelsize=8)
    ax.set_title(title, color=ACC, fontsize=13, fontweight="bold", loc="left", pad=11)
    if sub:
        ax.text(0, 1.012, sub, transform=ax.transAxes, color="#8b949e",
                fontsize=9, va="bottom")

fig.text(0.045, 0.962, "NURA ARES  ·  powered by AIME", color=FG,
         fontsize=21, fontweight="bold")
fig.text(0.045, 0.936, "ICU-in-a-Box — physical concept, DARPA DPA26BZ06-DV029   |   "
         "single integrated device · one ≤15 Fr central venous cannula · litter-mounted",
         color="#8b949e", fontsize=10.5)
fig.text(0.955, 0.962, "CONCEPT — NOT A BUILT DEVICE", color=ACC2,
         fontsize=11, fontweight="bold", ha="right")
fig.text(0.955, 0.940, "all dimensions engineering targets", color="#8b949e",
         fontsize=8.5, ha="right")

# ---------------------------------------------------------------- 1. THREE-VIEW
ax = fig.add_subplot(gs[0, 0]); style(ax, "01 — BASE UNIT  (three-view, mm)",
                                      "one box · litter-rail mounted · nothing bolted together")
ax.set_xlim(-70, 560); ax.set_ylim(-40, 330); ax.axis("off")
ax.add_patch(Rectangle((-60, -30), 610, 350, fill=False, ec=GRID, lw=.8, ls=(0,(4,4))))

def box(x, y, w, h, fc="#161b22", ec=ACC, lw=1.6, r=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r*max(w,h)}",
                                fc=fc, ec=ec, lw=lw))

# FRONT view 420 x 300
box(20, 150, 240, 150)
ax.text(140, 310, "FRONT", color=FG, fontsize=9, ha="center")
ax.add_patch(Rectangle((140, 240), 110, 48, fc="#0b1a26", ec=ACC2, lw=1.2))
ax.text(195, 264, '8" DISPLAY', color=ACC2, fontsize=7, ha="center")
for i in range(5):
    ax.add_patch(Rectangle((40+i*28, 210), 22, 16, fc="#1f2937", ec=ACC2, lw=.9))
ax.text(105, 199, "5 physical keys (glove-operable)", color="#8b949e", fontsize=6.5, ha="center")
for i, lab in enumerate(["ARTERIAL\n(cannula)", "VENOUS\n(cannula)"]):
    ax.add_patch(Circle((52+i*38, 172), 9, fc="none", ec=ACC, lw=1.6))
    ax.text(52+i*38, 150, lab, color="#8b949e", fontsize=5.8, ha="center")
ax.annotate("", xy=(20, 130), xytext=(260, 130),
            arrowprops=dict(arrowstyle="<->", color=ACC2, lw=1))
ax.text(140, 118, "420", color=ACC2, fontsize=8, ha="center")
ax.annotate("", xy=(272, 150), xytext=(272, 300),
            arrowprops=dict(arrowstyle="<->", color=ACC2, lw=1))
ax.text(280, 225, "300", color=ACC2, fontsize=8, rotation=90, va="center")

# SIDE view 180 deep
box(330, 150, 130, 150)
ax.text(395, 310, "SIDE", color=FG, fontsize=9, ha="center")
for i in range(2):
    ax.add_patch(Rectangle((340+i*36, 158), 32, 34, fc="#1f2937", ec=ACC, lw=1.2))
    ax.text(356+i*36, 175, "BAT", color=ACC, fontsize=6, ha="center")
ax.text(395, 200, "hot-swap\nbattery bays\n2 x 4 h", color="#8b949e", fontsize=6.5, ha="center")
ax.add_patch(Rectangle((352, 232), 86, 52, fc="#0b1a26", ec=ACC2, lw=1.1))
ax.text(395, 258, "O2 / LOX\ncylinder bay", color=ACC2, fontsize=6.5, ha="center")
ax.annotate("", xy=(330, 130), xytext=(460, 130),
            arrowprops=dict(arrowstyle="<->", color=ACC2, lw=1))
ax.text(395, 118, "180", color=ACC2, fontsize=8, ha="center")

# TOP view + rail clamps
box(20, 20, 240, 100, fc="#11161d")
ax.text(140, 130, "TOP", color=FG, fontsize=9, ha="center")
for i, x in enumerate((60, 240)):
    ax.add_patch(Rectangle((x-14, 30), 28, 80, fc="#1f2937", ec=ACC, lw=1.3))
ax.text(150, 68, "NATO litter-rail QD clamps (2x)", color=ACC, fontsize=6.8, ha="center")
ax.text(150, 52, "device rides WITH the casualty", color="#8b949e", fontsize=6.3, ha="center")

ax.text(330, 92, "DURABLE MASS", color=ACC, fontsize=9, fontweight="bold")
for i, (k, v) in enumerate([("pump + drive", 1.2), ("oxygenator + housing", 0.9),
                            ("circuit / manifold", 1.1), ("drug pumps (4-6)", 1.8),
                            ("sensors + cabling", 0.8), ("compute + safety governor", 0.7),
                            ("display + HMI", 0.6), ("chassis + thermal", 3.0)]):
    ax.text(330, 74-i*11, f"{k}", color="#8b949e", fontsize=6.8)
    ax.text(520, 74-i*11, f"{v:.1f} kg", color=FG, fontsize=6.8, ha="right")
ax.text(330, -8, "TOTAL (no battery/O2)", color=FG, fontsize=8, fontweight="bold")
ax.text(520, -8, "10.1 kg", color=ACC, fontsize=8, ha="right", fontweight="bold")

# ---------------------------------------------------------------- 2. DEPLOYMENT
ax = fig.add_subplot(gs[0, 1]); style(ax, "02 — DEPLOYMENT  (who carries what, in what order)",
                                      "designed for a medic who is already carrying 30 kg")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

# litter
ax.add_patch(FancyBboxPatch((10, 30), 78, 5, boxstyle="round,pad=0,rounding_size=1.2",
                            fc="#1f2937", ec=ACC2, lw=1.4))
for x in (16, 82):
    ax.add_patch(Circle((x, 32.5), 2.2, fc="none", ec=ACC2, lw=1.2))
ax.text(49, 24, "NATO standard litter", color=ACC2, fontsize=8, ha="center")
# patient
ax.add_patch(FancyBboxPatch((20, 36), 56, 9, boxstyle="round,pad=0,rounding_size=3",
                            fc="#15202b", ec=GRID, lw=1.2))
ax.add_patch(Circle((21, 40.5), 4, fc="#15202b", ec=GRID, lw=1.2))
ax.text(50, 40.5, "casualty", color="#8b949e", fontsize=7.5, ha="center", va="center")
# device clamped under litter
box_z = FancyBboxPatch((58, 45), 20, 9, boxstyle="round,pad=0,rounding_size=1.2",
                       fc="#0b1a26", ec=ACC, lw=1.8)
ax.add_patch(box_z)
ax.text(68, 49.5, "ARES", color=ACC, fontsize=8.5, ha="center", va="center", fontweight="bold")
ax.annotate("clamps to rail —\nno pole, no cart,\nno second operator",
            xy=(70, 45), xytext=(74, 68), color="#8b949e", fontsize=7,
            arrowprops=dict(arrowstyle="->", color=ACC, lw=1.1))
# cannula line
ax.annotate("", xy=(58, 47), xytext=(34, 43),
            arrowprops=dict(arrowstyle="-", color=ACC2, lw=1.6, ls="-"))
ax.text(44, 51, "one ≤15 Fr\ncentral cannula", color=ACC2, fontsize=6.8, ha="center")

seq = [
 ("1", "MEDIC: prime circuit, clamp to litter", "60-90 s"),
 ("2", "MEDIC: connect cannula (already placed)", "15 s"),
 ("3", "MEDIC: attach O2 + drug manifold", "45 s"),
 ("4", "PRESS START — medic's job is done", "—"),
 ("5", "ARES/AIME: autonomous from here", "24-72 h"),
]
ax.text(3, 91, "SETUP SEQUENCE", color=ACC, fontsize=9, fontweight="bold")
for i, (n, txt, t) in enumerate(seq):
    y = 84 - i*8.5
    ax.add_patch(Circle((5.5, y), 2.4, fc=ACC if i == 4 else "#1f2937", ec=ACC, lw=1.2))
    ax.text(5.5, y, n, color=BG if i == 4 else ACC, fontsize=7.5,
            ha="center", va="center", fontweight="bold")
    ax.text(10.5, y, txt, color=FG if i == 4 else "#8b949e", fontsize=7.6, va="center")
    ax.text(96, y, t, color=ACC2 if i < 4 else ACC, fontsize=7, ha="right", va="center")

ax.text(3, 36, "WHY LITTER-MOUNTED, NOT BACKPACK", color=ACC, fontsize=9, fontweight="bold")
for i, s in enumerate([
  "A combat medic already carries ~30 kg. Adding 10-15 kg breaks them.",
  "During evacuation the medic is not present — the device must travel with the patient.",
  "Litter mounting turns every stretcher into a rolling ICU with zero extra manpower.",
  "Consumables arrive by resupply, not on the operator's back."]):
    ax.text(3, 29-i*6, "•  " + s, color="#8b949e", fontsize=7.2, va="top", wrap=True)

# ---------------------------------------------------------------- 3. CIRCUIT
ax = fig.add_subplot(gs[1, 0]); style(ax, "03 — SINGLE-ACCESS FLUIDIC CIRCUIT",
                                      "one cannula in, one cannula out — every therapy injected upstream of return")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def nd(x, y, w, h, label, c=ACC2, fc="#0b1a26", fs=7):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4",
                                fc=fc, ec=c, lw=1.5))
    ax.text(x+w/2, y+h/2, label, color=c, fontsize=fs, ha="center", va="center")

# patient + dual lumen cannula
nd(4, 42, 20, 16, "PATIENT", c="#8b949e", fc="#15202b")
nd(28, 34, 15, 30, "dual-lumen\n≤15 Fr\ncannula", c=ACC, fs=6.5)
ax.annotate("", xy=(28, 56), xytext=(24, 50),
            arrowprops=dict(arrowstyle="->", color=ACC2, lw=1.7))
ax.annotate("", xy=(24, 44), xytext=(28, 44),
            arrowprops=dict(arrowstyle="->", color="#3fb950", lw=1.7))
ax.text(38, 68, "withdrawal →", color=ACC2, fontsize=6.5)
ax.text(12, 32, "← return", color="#3fb950", fontsize=6.5)

nd(47, 54, 20, 12, "PUMP\n2.5-3.5 L/min", c=ACC)
nd(47, 36, 20, 12, "OXYGENATOR\n+ gas blender", c=ACC)
ax.annotate("", xy=(57, 54), xytext=(57, 48),
            arrowprops=dict(arrowstyle="->", color=ACC2, lw=1.7))
ax.annotate("", xy=(47, 42), xytext=(43, 42),
            arrowprops=dict(arrowstyle="->", color=ACC2, lw=1.7))

nd(71, 54, 24, 12, "SAFETY GOVERNOR\nveto · limits", c="#f85149", fs=6.5)
ax.annotate("", xy=(71, 60), xytext=(67, 60),
            arrowprops=dict(arrowstyle="->", color="#f85149", lw=1.7))
ax.text(83, 70, "independent of AIME", color="#f85149", fontsize=6.3, ha="center")

# therapeutic manifold
nd(71, 30, 24, 16, "THERAPEUTIC\nMANIFOLD", c="#3fb950", fs=6.8)
for i, d in enumerate(["vasopressor", "sedation/analgesia", "anticoagulation", "blood / crystalloid"]):
    ax.text(97, 43-i*4.2, "• " + d, color="#8b949e", fontsize=6.2, ha="right")
ax.annotate("", xy=(71, 38), xytext=(67, 42),
            arrowprops=dict(arrowstyle="->", color="#3fb950", lw=1.7))
ax.annotate("", xy=(40, 46), xytext=(71, 30),
            arrowprops=dict(arrowstyle="->", color="#3fb950", lw=1.3,
                            connectionstyle="arc3,rad=-0.25"))
ax.text(54, 22, "all drugs/blood enter the RETURN limb → membrane never alters dose",
        color="#3fb950", fontsize=6.4, ha="center")

nd(28, 6, 44, 10, "O2 SOURCE  —  cylinder | LOX | concentrator", c=ACC2, fs=6.8)
ax.annotate("", xy=(57, 36), xytext=(57, 16),
            arrowprops=dict(arrowstyle="->", color=ACC2, lw=1.5))

# ---------------------------------------------------------------- 4. SWAP
ax = fig.add_subplot(gs[1, 1]); style(ax, "04 — THE FINDING THE BLUEPRINT MISSED:  mass is dominated by gas & power",
                                      "blueprint budgeted volumes; never budgeted kilograms")
labels = ["pump\ndrive", "oxyg-\nenator", "circuit\nmanifold", "drug\npumps",
          "sensors", "compute\ngovernor", "display", "chassis", "battery\n8h@300W", "O2 24h\n(steel cyl)"]
vals =   [1.2,          0.9,           1.1,              1.8,
          0.8,          0.7,            0.6,         3.0,     11.3,          14.4]
cols = [ACC2]*8 + [ACC, "#f85149"]
bars = ax.bar(range(len(vals)), vals, color=cols, width=.68,
              edgecolor=BG, linewidth=.8)
ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels, fontsize=7.4, color=FG)
ax.set_ylabel("kilograms", color=FG, fontsize=9)
ax.grid(axis="y", color=GRID, lw=.6, ls=(0,(3,3))); ax.set_axisbelow(True)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+.35, f"{v:.1f}", ha="center",
            color=FG, fontsize=7.6, fontweight="bold")
ax.axhline(12, color=ACC, lw=1.4, ls="--")
ax.text(9.4, 12.6, "blueprint M24 target  12 kg", color=ACC, fontsize=8, ha="right")
ax.axhline(8, color=ACC2, lw=1.2, ls=":")
ax.text(9.4, 8.6, "stretch  8 kg", color=ACC2, fontsize=8, ha="right")
ax.set_ylim(0, 18.5)
ax.text(0.02, 0.97,
        "34.99 kg for a 24-hour mission — 2.9x the target.\n"
        "Gas and power alone = 25.7 kg (73%).\n"
        "LOX instead of steel  ->  saves 9.4 kg (5.0 kg vs 14.4)\n"
        "72 h on cylinders     ->  ~45 kg of oxygen alone.\n"
        "CONCLUSION: ARES is not a backpack. It is a litter-mounted\n"
        "device with a resupply tail; M9 form only for 2-4 h hops.",
        transform=ax.transAxes, color=FG, fontsize=8.1, va="top",
        bbox=dict(boxstyle="round,pad=0.55", fc="#161b22", ec=GRID))
ax.set_title("04 — THE FINDING THE BLUEPRINT MISSED", color=ACC,
             fontsize=13, fontweight="bold", loc="left", pad=26)
ax.text(0, 1.055, "blueprint budgeted volumes; never budgeted kilograms",
        transform=ax.transAxes, color="#8b949e", fontsize=9, va="bottom")
ax.set_title("", pad=22)

fig.text(0.045, 0.014,
  "ENGINEERING CONCEPT — not a built device. Masses are first-order estimates at planning fidelity. "
  "Sources: inert gas pV=nRT at 200/300 bar; LOX 1.141 kg/L, 860 L gas/L; battery 250 Wh/kg pack, 85% usable; "
  "concentrator 90% O2 @ ~1 L/min per ~100 W.",
  color="#8b949e", fontsize=7.4)

out = "/opt/data/ares_render.png"
fig.savefig(out, dpi=165, facecolor=BG)
print("saved:", out)
