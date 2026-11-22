import os
import math
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

os.makedirs("output/dxf", exist_ok=True)
os.makedirs("output/png", exist_ok=True)

# ---------------------------------------------------------
# SHARED GEOMETRY & CONSTANTS (meters)
# ---------------------------------------------------------
LOT_W = 12.50
LOT_L = 30.00

# Structural Grid
GRID_X = [0.25, 4.25, 8.25, 12.25]          # A, B, C, D
GRID_Y = [0.25, 5.75, 11.75, 17.75, 23.75, 29.75]  # 1, 2, 3, 4, 5, 6
COL_SIZE = 0.40

# Fixed Core (Elevator + Stairs + MEP Ducts) on ALL 6 floors
# Located centrally between X=4.25..8.25, Y=17.75..23.75
ELEV_RECT = (4.45, 18.00, 1.80, 2.00)       # x, y, w, h (8-person elevator)
STAIR_RECT = (4.45, 20.00, 2.60, 3.55)      # x, y, w, h (2-flight stair)
DUCT_1 = (7.25, 18.00, 0.80, 1.00)          # MEP Shaft 1
DUCT_2 = (7.25, 22.55, 0.80, 1.00)          # MEP Shaft 2

# Lightwell (Patio / Noorgir) for upper floors & ground janitor
PATIO_RECT = (8.45, 18.00, 3.60, 3.40)      # 3.60 x 3.40 = 12.24 m2 (>= 12 m2)

# Ramp Geometry (West side: X=0.25..3.75, width=3.50m)
RAMP_RECT = (0.25, 1.00, 3.50, 20.00)       # Y=1.00 to Y=21.00

# ---------------------------------------------------------
# HELPER: DXF GENERATOR
# ---------------------------------------------------------
def create_dxf_base():
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    layers = [
        ("LOT_BOUNDARY", 8),
        ("GRID", 9),
        ("COLUMNS", 1),
        ("WALLS", 7),
        ("DOORS_WINDOWS", 3),
        ("STAIRS_ELEV", 4),
        ("PARKING_RAMP", 5),
        ("MEP_DUCTS", 6),
        ("TEXT_DIM", 2),
    ]
    for name, color in layers:
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    return doc, msp

def dxf_rect(msp, x, y, w, h, layer):
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer})

def dxf_text(msp, x, y, text, height=0.25, layer="TEXT_DIM"):
    msp.add_text(text, dxfattribs={"height": height, "layer": layer}).set_placement((x, y))

# ---------------------------------------------------------
# HELPER: MATPLOTLIB ARCHITECTURAL RENDERER
# ---------------------------------------------------------
def setup_plan_ax(fig, title, subtitle):
    ax = fig.add_axes([0.06, 0.06, 0.62, 0.84])
    ax.set_xlim(-1.2, LOT_W + 1.2)
    ax.set_ylim(-1.5, LOT_L + 1.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # Lot boundary
    ax.add_patch(patches.Rectangle((0, 0), LOT_W, LOT_L, fill=False, edgecolor="#111827", linewidth=2.0))

    # Structural Grid lines
    labels_x = ["A", "B", "C", "D"]
    for i, gx in enumerate(GRID_X):
        ax.plot([gx, gx], [-0.6, LOT_L + 0.6], linestyle="-.", color="#cbd5e1", linewidth=0.6, zorder=1)
        ax.text(gx, LOT_L + 0.85, labels_x[i], ha="center", va="center", fontsize=8, fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.2", fc="#f1f5f9", ec="#64748b", lw=0.7))
    for j, gy in enumerate(GRID_Y):
        ax.plot([-0.6, LOT_W + 0.6], [gy, gy], linestyle="-.", color="#cbd5e1", linewidth=0.6, zorder=1)
        ax.text(-0.85, gy, str(j + 1), ha="center", va="center", fontsize=8, fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.2", fc="#f1f5f9", ec="#64748b", lw=0.7))

    # Street label (South)
    ax.text(LOT_W / 2, -1.05, "SOUTH STREET (12.50 m Frontage)", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#334155")

    # Title block on right
    fig.text(0.71, 0.87, title, fontsize=14, fontweight="bold", color="#0f172a")
    fig.text(0.71, 0.835, subtitle, fontsize=9.5, color="#475569")
    return ax

def draw_columns(ax, msp, y_indices=range(len(GRID_Y))):
    for gx in GRID_X:
        for idx in y_indices:
            gy = GRID_Y[idx]
            x0, y0 = gx - COL_SIZE / 2, gy - COL_SIZE / 2
            ax.add_patch(patches.Rectangle((x0, y0), COL_SIZE, COL_SIZE, facecolor="#1e293b", edgecolor="#0f172a", zorder=5))
            dxf_rect(msp, x0, y0, COL_SIZE, COL_SIZE, "COLUMNS")

def draw_core(ax, msp):
    # Elevator
    ex, ey, ew, eh = ELEV_RECT
    ax.add_patch(patches.Rectangle((ex, ey), ew, eh, facecolor="#e0f2fe", edgecolor="#0284c7", linewidth=1.3, zorder=3))
    ax.plot([ex, ex + ew], [ey, ey + eh], color="#0284c7", linewidth=0.7, zorder=3)
    ax.plot([ex, ex + ew], [ey + eh, ey], color="#0284c7", linewidth=0.7, zorder=3)
    ax.text(ex + ew / 2, ey + eh / 2, "ELEV\n(8P)", ha="center", va="center", fontsize=6.5, fontweight="bold", color="#0369a1", zorder=4)
    dxf_rect(msp, ex, ey, ew, eh, "STAIRS_ELEV")
    dxf_text(msp, ex + 0.2, ey + eh / 2, "ELEV 8P", 0.22, "STAIRS_ELEV")

    # Stairs
    sx, sy, sw, sh = STAIR_RECT
    ax.add_patch(patches.Rectangle((sx, sy), sw, sh, facecolor="#f8fafc", edgecolor="#334155", linewidth=1.3, zorder=3))
    for k in range(1, 10):
        ty = sy + k * (sh / 10.0)
        ax.plot([sx, sx + sw], [ty, ty], color="#94a3b8", linewidth=0.5, zorder=3)
    ax.plot([sx + sw / 2, sx + sw / 2], [sy + 0.3, sy + sh - 0.3], color="#475569", linewidth=1.0, zorder=3)
    ax.text(sx + sw / 2, sy + sh / 2, "STAIRCASE", ha="center", va="center", fontsize=6.5, fontweight="bold", color="#1e293b", zorder=4,
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.8))
    dxf_rect(msp, sx, sy, sw, sh, "STAIRS_ELEV")
    dxf_text(msp, sx + 0.3, sy + sh / 2, "STAIRS", 0.25, "STAIRS_ELEV")

    # MEP Ducts
    for idx, (dx, dy, dw, dh) in enumerate([DUCT_1, DUCT_2], 1):
        ax.add_patch(patches.Rectangle((dx, dy), dw, dh, facecolor="#fae8ff", edgecolor="#9333ea", linewidth=1.0, hatch="///", zorder=3))
        ax.text(dx + dw / 2, dy + dh / 2, f"MEP\nD{idx}", ha="center", va="center", fontsize=5.5, fontweight="bold", color="#6b21a8", zorder=4)
        dxf_rect(msp, dx, dy, dw, dh, "MEP_DUCTS")

def draw_room(ax, msp, x, y, w, h, label, fc="#ffffff", ec="#334155", lw=1.2, fs=6.8):
    ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs, color="#0f172a", zorder=4)
    dxf_rect(msp, x, y, w, h, "WALLS")
    dxf_text(msp, x + 0.2, y + h / 2, label.replace("\n", " "), 0.22, "TEXT_DIM")

def draw_parking_bay(ax, msp, x, y, w, h, label):
    ax.add_patch(patches.Rectangle((x, y), w, h, facecolor="#dbeafe", edgecolor="#1d4ed8", linewidth=1.2, linestyle="--", zorder=2))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=7, fontweight="bold", color="#1e3a8a", zorder=4)
    dxf_rect(msp, x, y, w, h, "PARKING_RAMP")
    dxf_text(msp, x + 0.3, y + h / 2, label, 0.25, "PARKING_RAMP")

def add_notes_panel(fig, notes):
    y_pos = 0.78
    for heading, lines in notes:
        fig.text(0.71, y_pos, heading, fontsize=9.5, fontweight="bold", color="#1e293b")
        y_pos -= 0.025
        for ln in lines:
            fig.text(0.715, y_pos, f"• {ln}", fontsize=8, color="#334155")
            y_pos -= 0.022
        y_pos -= 0.015

# ---------------------------------------------------------
# 1. BASEMENT -1 PLAN
# ---------------------------------------------------------
def build_basement(pdf):
    doc, msp = create_dxf_base()
    fig = plt.figure(figsize=(11.69, 8.27))  # A3/A4 Landscape
    ax = setup_plan_ax(fig, "LEVEL -1: BASEMENT PLAN", "Scale 1:100 | Clear Height: 2.60 m | Slab-to-Slab: 3.00 m")

    # Perimeter retaining wall
    draw_room(ax, msp, 0.15, 0.15, LOT_W - 0.30, LOT_L - 0.30, "", fc="#f8fafc", ec="#0f172a", lw=2.0)

    # Ramp arrival (West)
    rx, ry, rw, rh = RAMP_RECT
    ax.add_patch(patches.Rectangle((rx, ry), rw, rh, facecolor="#fef3c7", edgecolor="#d97706", linewidth=1.3, zorder=2))
    ax.annotate("", xy=(rx + rw / 2, ry + rh - 0.8), xytext=(rx + rw / 2, ry + 1.0),
                arrowprops=dict(arrowstyle="->", color="#b45309", lw=2.0), zorder=4)
    ax.text(rx + rw / 2, ry + rh / 2, "RAMP DOWN\n15% Slope\nL=18.0m + Landings\ndH <= 60cm at\nTransition",
            ha="center", va="center", fontsize=6.8, fontweight="bold", color="#92400e", zorder=4)
    dxf_rect(msp, rx, ry, rw, rh, "PARKING_RAMP")

    # 4 Independent Parking Bays (East & North-East)
    draw_parking_bay(ax, msp, 7.25, 24.50, 2.50, 5.00, "P1\n2.5x5.0m")
    draw_parking_bay(ax, msp, 9.75, 24.50, 2.50, 5.00, "P2\n2.5x5.0m")
    draw_parking_bay(ax, msp, 7.25, 11.75, 2.50, 5.00, "P3\n2.5x5.0m")
    draw_parking_bay(ax, msp, 9.75, 11.75, 2.50, 5.00, "P4\n2.5x5.0m")

    # Maneuvering Aisle label
    ax.text(8.80, 20.50, "MANEUVERING AISLE\n(6.0m Clear Width)", ha="center", va="center",
            fontsize=7, fontweight="bold", color="#475569", style="italic")

    # Mechanical / Boiler & Pump Room (South-East)
    draw_room(ax, msp, 7.25, 0.40, 4.90, 4.80, "MECHANICAL & PUMP ROOM\n(4.90 x 4.80 m)\nBoiler, Booster Pumps, Tanks",
              fc="#fee2e2", ec="#b91c1c", fs=6.5)

    # 8 Independent Storage Rooms (Anbari 1-8) adjacent to MEP
    for i in range(4):
        sx = 4.25 + i * 2.00
        draw_room(ax, msp, sx, 5.75, 1.95, 2.40, f"Storage {i+1}\n2.0x2.4m", fc="#ecfdf5", ec="#047857", fs=5.8)
        draw_room(ax, msp, sx, 8.25, 1.95, 2.40, f"Storage {i+5}\n2.0x2.4m", fc="#ecfdf5", ec="#047857", fs=5.8)

    draw_core(ax, msp)
    draw_columns(ax, msp)

    add_notes_panel(fig, [
        ("Parking & Ramp Verification", [
            "4 independent bays (P1-P4), 2.50 x 5.00 m each.",
            "6.00 m clear maneuvering aisle; zero blocking.",
            "Ramp: 15% slope (18.0 m) + 2.0 m landings.",
            "Transition step/curb dH <= 60 cm at Y=21.0 m.",
            "Clear height: 2.60 m (>= 2.50 m required)."
        ]),
        ("Storage & MEP", [
            "8 independent storage rooms (4.7 m2 each).",
            "Clustered near Mechanical & Pump Room.",
            "Direct access to Elevator (8P) & Staircase."
        ])
    ])

    doc.saveas("output/dxf/01_basement.dxf")
    pdf.savefig(fig)
    plt.close(fig)

# ---------------------------------------------------------
# 2. GROUND FLOOR PLAN
# ---------------------------------------------------------
def build_ground(pdf):
    doc, msp = create_dxf_base()
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = setup_plan_ax(fig, "LEVEL 00: GROUND FLOOR PLAN", "Scale 1:100 | 4 Parking + Janitor Unit + Main Entrance")

    # Ramp (West)
    rx, ry, rw, rh = RAMP_RECT
    ax.add_patch(patches.Rectangle((rx, ry), rw, rh, facecolor="#fef3c7", edgecolor="#d97706", linewidth=1.3, zorder=2))
    ax.text(rx + rw / 2, ry + 5.0, "RAMP TO B-1\n(15% Down)\ndH <= 60cm\nat Entrance", ha="center", va="center",
            fontsize=6.8, fontweight="bold", color="#92400e", zorder=4)
    dxf_rect(msp, rx, ry, rw, rh, "PARKING_RAMP")

    # 4 Independent Parking Bays (South Yard, East of Ramp)
    draw_parking_bay(ax, msp, 4.30, 0.50, 2.50, 5.00, "P5\n2.5x5.0m")
    draw_parking_bay(ax, msp, 6.90, 0.50, 2.50, 5.00, "P6\n2.5x5.0m")
    draw_parking_bay(ax, msp, 9.50, 0.50, 2.50, 5.00, "P7\n2.5x5.0m")
    draw_parking_bay(ax, msp, 9.50, 6.20, 2.50, 5.00, "P8\n2.5x5.0m")

    # Main Building Entrance & Lobby
    draw_room(ax, msp, 4.25, 11.75, 4.00, 6.00, "MAIN ENTRANCE\n& LOBBY\n(4.00 x 6.00 m)", fc="#f1f5f9", ec="#0f172a", fs=7)

    # Janitor 1-Bedroom Unit (North-East & North)
    draw_room(ax, msp, 0.25, 21.50, 4.00, 8.25, "JANITOR UNIT (45 m2)\nLiving + Open Kitchen\n(4.00 x 4.50 m)", fc="#fefce8", ec="#854d0e", fs=6.5)
    draw_room(ax, msp, 8.25, 23.75, 4.00, 6.00, "JANITOR BEDROOM\n(4.00 x 4.20 m)\n+ Bath", fc="#fefce8", ec="#854d0e", fs=6.5)

    # Lightwell / Patio
    px, py, pw, ph = PATIO_RECT
    ax.add_patch(patches.Rectangle((px, py), pw, ph, facecolor="#e0f2fe", edgecolor="#0284c7", linestyle="--", zorder=2))
    ax.text(px + pw / 2, py + ph / 2, "LIGHTWELL\n3.6 x 3.4 m", ha="center", va="center", fontsize=6.5, color="#0369a1", zorder=4)

    draw_core(ax, msp)
    draw_columns(ax, msp)

    add_notes_panel(fig, [
        ("Ground Floor Program", [
            "4 independent parking bays (P5-P8) in South yard.",
            "Zero interference with Ramp or Main Lobby.",
            "1-Bedroom Janitor Unit (~45 m2) on North side.",
            "Natural light via North facade & Lightwell."
        ]),
        ("Vertical Core", [
            "8-Person Elevator + 2-Flight Staircase.",
            "Exact same coordinates as Basement -1."
        ])
    ])

    doc.saveas("output/dxf/02_ground.dxf")
    pdf.savefig(fig)
    plt.close(fig)

# ---------------------------------------------------------
# 3. FIRST FLOOR PLAN (1x 2-Bed + 1x 1-Bed)
# ---------------------------------------------------------
def build_first_floor(pdf):
    doc, msp = create_dxf_base()
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = setup_plan_ax(fig, "LEVEL 01: FIRST FLOOR PLAN", "Scale 1:100 | Unit 1 (2-Bed, 115 m2) + Unit 2 (1-Bed, 75 m2)")

    # South Yard (open below)
    ax.text(LOT_W / 2, 5.75, "OPEN SOUTH YARD BELOW", ha="center", va="center", fontsize=8, color="#94a3b8", style="italic")

    # UNIT 1 (South, 2-Bedroom, 115 m2)
    draw_room(ax, msp, 0.25, 11.75, 4.00, 2.00, "TERRACE (4.0x2.0m)", fc="#dcfce7", ec="#15803d", fs=6)
    draw_room(ax, msp, 0.25, 13.75, 4.00, 4.00, "U1: OPEN ISLAND\nKITCHEN", fc="#fff7ed", ec="#c2410c", fs=6.5)
    draw_room(ax, msp, 4.25, 11.75, 4.00, 6.00, "U1: LIVING & DINING\n(4.00 x 6.00 m)", fc="#ffffff", ec="#334155", fs=6.8)
    draw_room(ax, msp, 8.25, 11.75, 4.00, 3.50, "U1: MASTER BED\n+ En-Suite & WIC", fc="#eff6ff", ec="#1d4ed8", fs=6.2)
    draw_room(ax, msp, 8.25, 15.25, 4.00, 2.75, "U1: BEDROOM 2\n+ Bath & Laundry", fc="#eff6ff", ec="#1d4ed8", fs=6.2)

    # UNIT 2 (North, 1-Bedroom, 75 m2)
    draw_room(ax, msp, 0.25, 23.75, 4.00, 6.00, "U2: LIVING & DINING\n+ Island Kitchen\n& Terrace", fc="#ffffff", ec="#334155", fs=6.5)
    draw_room(ax, msp, 4.25, 23.75, 4.00, 6.00, "U2: MASTER BEDROOM\n+ En-Suite & Laundry", fc="#eff6ff", ec="#1d4ed8", fs=6.5)
    draw_room(ax, msp, 8.25, 23.75, 4.00, 6.00, "U2: TERRACE & STUDY", fc="#dcfce7", ec="#15803d", fs=6.5)

    # Lightwell
    px, py, pw, ph = PATIO_RECT
    ax.add_patch(patches.Rectangle((px, py), pw, ph, facecolor="#e0f2fe", edgecolor="#0284c7", linestyle="--", zorder=2))
    ax.text(px + pw / 2, py + ph / 2, "LIGHTWELL\n3.6 x 3.4 m", ha="center", va="center", fontsize=6.5, color="#0369a1", zorder=4)

    draw_core(ax, msp)
    draw_columns(ax, msp, y_indices=[2, 3, 4, 5])

    add_notes_panel(fig, [
        ("Unit 1 (South - 2 Bedroom)", [
            "Area: ~115 m2 | Clear Height: 3.00 m.",
            "Master Bedroom with En-Suite & Walk-in Closet.",
            "Open Island Kitchen adjacent to Terrace.",
            "Private bedroom zone separated from Living."
        ]),
        ("Unit 2 (North - 1 Bedroom)", [
            "Area: ~75 m2 | Clear Height: 3.00 m.",
            "Master Bedroom, Open Kitchen, Terrace, Laundry."
        ])
    ])

    doc.saveas("output/dxf/03_first_floor.dxf")
    pdf.savefig(fig)
    plt.close(fig)

# ---------------------------------------------------------
# 4. SECOND FLOOR PLAN (1x 4-Bedroom Luxury Unit)
# ---------------------------------------------------------
def build_second_floor(pdf):
    doc, msp = create_dxf_base()
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = setup_plan_ax(fig, "LEVEL 02: SECOND FLOOR PLAN", "Scale 1:100 | Unit 3 (Full-Floor 4-Bedroom, 200 m2)")

    ax.text(LOT_W / 2, 5.75, "OPEN SOUTH YARD BELOW", ha="center", va="center", fontsize=8, color="#94a3b8", style="italic")

    # Full-floor 4-Bedroom
    draw_room(ax, msp, 0.25, 11.75, 4.00, 2.00, "SOUTH TERRACE", fc="#dcfce7", ec="#15803d", fs=6.5)
    draw_room(ax, msp, 0.25, 13.75, 4.00, 4.00, "OPEN ISLAND\nKITCHEN + LAUNDRY", fc="#fff7ed", ec="#c2410c", fs=6.5)
    draw_room(ax, msp, 4.25, 11.75, 8.00, 6.00, "GRAND LIVING & DINING HALL\n(8.00 x 6.00 m = 48 m2)", fc="#ffffff", ec="#334155", fs=7.5)

    draw_room(ax, msp, 0.25, 17.75, 4.00, 6.00, "MASTER SUITE\n+ Walk-in Closet\n+ Master Bath", fc="#eff6ff", ec="#1d4ed8", fs=6.5)
    draw_room(ax, msp, 0.25, 23.75, 4.00, 6.00, "BEDROOM 2\n(En-Suite)", fc="#eff6ff", ec="#1d4ed8", fs=6.5)
    draw_room(ax, msp, 4.25, 23.75, 4.00, 6.00, "BEDROOM 3\n+ Main Bath", fc="#eff6ff", ec="#1d4ed8", fs=6.5)
    draw_room(ax, msp, 8.25, 23.75, 4.00, 6.00, "BEDROOM 4\n+ North Terrace", fc="#eff6ff", ec="#1d4ed8", fs=6.5)

    px, py, pw, ph = PATIO_RECT
    ax.add_patch(patches.Rectangle((px, py), pw, ph, facecolor="#e0f2fe", edgecolor="#0284c7", linestyle="--", zorder=2))
    ax.text(px + pw / 2, py + ph / 2, "LIGHTWELL\n3.6 x 3.4 m", ha="center", va="center", fontsize=6.5, color="#0369a1", zorder=4)

    draw_core(ax, msp)
    draw_columns(ax, msp, y_indices=[2, 3, 4, 5])

    add_notes_panel(fig, [
        ("Unit 3 (Full-Floor 4-Bedroom)", [
            "Area: ~200 m2 | Clear Height: 3.00 m.",
            "4 Bedrooms: 1 Master Suite + 3 Bedrooms.",
            "48 m2 Grand Living/Dining facing South.",
            "Open Island Kitchen + Terrace + Laundry.",
            "All bedrooms naturally lit & ventilated."
        ])
    ])

    doc.saveas("output/dxf/04_second_floor.dxf")
    pdf.savefig(fig)
    plt.close(fig)

# ---------------------------------------------------------
# 5 & 6. THIRD & FOURTH FLOOR PLANS (2x 2-Bedroom each)
# ---------------------------------------------------------
def build_typical_two_unit(pdf, level_num, title, subtitle, dxf_name):
    doc, msp = create_dxf_base()
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = setup_plan_ax(fig, title, subtitle)

    ax.text(LOT_W / 2, 5.75, "OPEN SOUTH YARD BELOW", ha="center", va="center", fontsize=8, color="#94a3b8", style="italic")

    # South 2-Bed Unit (~105 m2)
    draw_room(ax, msp, 0.25, 11.75, 4.00, 2.00, "TERRACE", fc="#dcfce7", ec="#15803d", fs=6.5)
    draw_room(ax, msp, 0.25, 13.75, 4.00, 4.00, "SOUTH UNIT:\nISLAND KITCHEN", fc="#fff7ed", ec="#c2410c", fs=6.5)
    draw_room(ax, msp, 4.25, 11.75, 4.00, 6.00, "SOUTH UNIT:\nLIVING & DINING", fc="#ffffff", ec="#334155", fs=6.8)
    draw_room(ax, msp, 8.25, 11.75, 4.00, 3.50, "SOUTH UNIT:\nMASTER BED + Bath", fc="#eff6ff", ec="#1d4ed8", fs=6.2)
    draw_room(ax, msp, 8.25, 15.25, 4.00, 2.75, "SOUTH UNIT:\nBEDROOM 2 + Laundry", fc="#eff6ff", ec="#1d4ed8", fs=6.0)

    # North 2-Bed Unit (~95 m2)
    draw_room(ax, msp, 0.25, 23.75, 4.00, 6.00, "NORTH UNIT:\nLIVING + ISLAND KITCHEN\n& TERRACE", fc="#ffffff", ec="#334155", fs=6.2)
    draw_room(ax, msp, 4.25, 23.75, 4.00, 6.00, "NORTH UNIT:\nMASTER BED + Bath", fc="#eff6ff", ec="#1d4ed8", fs=6.5)
    draw_room(ax, msp, 8.25, 23.75, 4.00, 6.00, "NORTH UNIT:\nBEDROOM 2 + Laundry", fc="#eff6ff", ec="#1d4ed8", fs=6.5)

    px, py, pw, ph = PATIO_RECT
    ax.add_patch(patches.Rectangle((px, py), pw, ph, facecolor="#e0f2fe", edgecolor="#0284c7", linestyle="--", zorder=2))
    ax.text(px + pw / 2, py + ph / 2, "LIGHTWELL\n3.6 x 3.4 m", ha="center", va="center", fontsize=6.5, color="#0369a1", zorder=4)

    draw_core(ax, msp)
    draw_columns(ax, msp, y_indices=[2, 3, 4, 5])

    add_notes_panel(fig, [
        (f"Level {level_num} Program", [
            "2x Two-Bedroom Units (~105 m2 & ~95 m2).",
            "Each unit has at least 1 Master Bedroom.",
            "Open Island Kitchen + adjacent Terrace.",
            "100% aligned columns, core, and MEP shafts."
        ])
    ])

    doc.saveas(f"output/dxf/{dxf_name}")
    pdf.savefig(fig)
    plt.close(fig)

# ---------------------------------------------------------
# COVER & ENGINEERING SUMMARY PAGE
# ---------------------------------------------------------
def build_cover(pdf):
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.08, 0.88, "8-UNIT MODERN MINIMALIST RESIDENTIAL BUILDING", fontsize=18, fontweight="bold", color="#0f172a")
    fig.text(0.08, 0.84, "Architectural, Structural & MEP Coordinated Floor Plans (Lot: 12.50 m x 30.00 m)", fontsize=11, color="#475569")

    summary_blocks = [
        ("1. Project Specifications", [
            "Lot Dimensions: 12.50 m (W) x 30.00 m (L) = 375.0 m2 | Flat Northern Lot",
            "Levels: 6 Total (Basement -1, Ground, 1st, 2nd, 3rd, 4th) | 8 Residential Units",
            "Structure: Reinforced Concrete (RC) Frame | 3x5 Structural Grid (40x40 cm Columns)",
            "Floor-to-Floor Height: 3.50 m (Upper) / 3.00 m (Basement -1) | Clear Height: 3.00 m / 2.60 m"
        ]),
        ("2. Parking & Ramp Engineering (Verified)", [
            "Total Independent Parking: 8 Spaces (4 on Ground P5-P8 + 4 on Basement -1 P1-P4)",
            "Zero-blocking layout: Every vehicle enters and exits independently (6.0 m aisle)",
            "Ramp: 3.50 m width, 15% slope (18.0 m) + 2.0 m top/bottom transition landings",
            "Max Height Difference at Ramp-Parking Transition: dH <= 60 cm (annotated on plans)"
        ]),
        ("3. Core, MEP & Natural Light", [
            "Fixed Vertical Core: 8-Person Elevator (1.80x2.00 m) + 2-Flight Staircase (2.60x3.55 m)",
            "Fixed MEP Shafts: 2 vertical risers (D1, D2) aligned on all 6 levels",
            "8 Independent Storage Rooms + Mechanical/Pump Room in Basement -1",
            "Central-East Lightwell (3.60 x 3.40 m = 12.24 m2) ensures natural light & ventilation"
        ])
    ]
    y = 0.75
    for title, items in summary_blocks:
        fig.text(0.08, y, title, fontsize=11.5, fontweight="bold", color="#1e293b")
        y -= 0.032
        for it in items:
            fig.text(0.10, y, f"• {it}", fontsize=9.5, color="#334155")
            y -= 0.026
        y -= 0.025

    fig.text(0.08, 0.12, "Deliverables: Multi-page Vector PDF + 6 Editable AutoCAD DXF Files (output/dxf/)", fontsize=9.5, fontweight="bold", color="#0369a1")
    pdf.savefig(fig)
    plt.close(fig)

# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
pdf_path = "output/Residential_8Unit_Architectural_Plans.pdf"
with PdfPages(pdf_path) as pdf:
    build_cover(pdf)
    build_basement(pdf)
    build_ground(pdf)
    build_first_floor(pdf)
    build_second_floor(pdf)
    build_typical_two_unit(pdf, "03", "LEVEL 03: THIRD FLOOR PLAN", "Scale 1:100 | 2x 2-Bedroom Units (105 m2 & 95 m2)", "05_third_floor.dxf")
    build_typical_two_unit(pdf, "04", "LEVEL 04: FOURTH FLOOR PLAN", "Scale 1:100 | 2x 2-Bedroom Units (105 m2 & 95 m2)", "06_fourth_floor.dxf")

print("Generated:", pdf_path)
