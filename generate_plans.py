import os
import ezdxf

os.makedirs("output/dxf", exist_ok=True)

LOT_W = 12.50
LOT_L = 30.00
GRID_X = [0.25, 4.25, 8.25, 12.25]
GRID_Y = [0.25, 5.75, 11.75, 17.75, 23.75, 29.75]
COL_SIZE = 0.40

ELEV_RECT = (4.45, 18.00, 1.80, 2.00)
STAIR_RECT = (4.45, 20.00, 2.60, 3.55)
DUCT_1 = (7.25, 18.00, 0.80, 1.00)
DUCT_2 = (7.25, 22.55, 0.80, 1.00)
PATIO_RECT = (8.45, 18.00, 3.60, 3.40)
RAMP_RECT = (0.25, 1.00, 3.50, 20.00)


def setup_doc():
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.M
    layers = [
        ("00_LOT", 8),
        ("01_GRID", 9),
        ("02_COLUMNS", 1),
        ("03_WALLS_EXT", 7),
        ("04_WALLS_INT", 7),
        ("05_DOORS", 3),
        ("06_WINDOWS", 4),
        ("07_STAIRS_ELEV", 4),
        ("08_PARKING_RAMP", 5),
        ("09_MEP_DUCTS", 6),
        ("10_DIMENSIONS", 2),
        ("11_TEXT", 2),
        ("12_FURNITURE", 8),
    ]
    for name, color in layers:
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    return doc


def rect(msp, ox, oy, x, y, w, h, layer):
    pts = [(ox + x, oy + y), (ox + x + w, oy + y), (ox + x + w, oy + y + h), (ox + x, oy + y + h), (ox + x, oy + y)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer})


def wall_box(msp, ox, oy, x, y, w, h, t=0.15, layer="04_WALLS_INT"):
    rect(msp, ox, oy, x, y, w, h, layer)
    if w > 2 * t and h > 2 * t:
        rect(msp, ox, oy, x + t, y + t, w - 2 * t, h - 2 * t, layer)


def txt(msp, ox, oy, x, y, s, h=0.20, layer="11_TEXT"):
    msp.add_text(s, dxfattribs={"height": h, "layer": layer}).set_placement((ox + x, oy + y))


def dim_h(msp, ox, oy, x1, x2, y, label=None):
    msp.add_line((ox + x1, oy + y), (ox + x2, oy + y), dxfattribs={"layer": "10_DIMENSIONS"})
    msp.add_line((ox + x1, oy + y - 0.15), (ox + x1, oy + y + 0.15), dxfattribs={"layer": "10_DIMENSIONS"})
    msp.add_line((ox + x2, oy + y - 0.15), (ox + x2, oy + y + 0.15), dxfattribs={"layer": "10_DIMENSIONS"})
    val = label if label else f"{abs(x2 - x1):.2f}m"
    txt(msp, ox, oy, (x1 + x2) / 2 - 0.4, y + 0.12, val, h=0.20, layer="10_DIMENSIONS")


def dim_v(msp, ox, oy, y1, y2, x, label=None):
    msp.add_line((ox + x, oy + y1), (ox + x, oy + y2), dxfattribs={"layer": "10_DIMENSIONS"})
    msp.add_line((ox + x - 0.15, oy + y1), (ox + x + 0.15, oy + y1), dxfattribs={"layer": "10_DIMENSIONS"})
    msp.add_line((ox + x - 0.15, oy + y2), (ox + x + 0.15, oy + y2), dxfattribs={"layer": "10_DIMENSIONS"})
    val = label if label else f"{abs(y2 - y1):.2f}m"
    txt(msp, ox, oy, x + 0.12, (y1 + y2) / 2, val, h=0.20, layer="10_DIMENSIONS")


def door(msp, ox, oy, x, y, w=0.90, direction="NE"):
    # Draws door leaf + 90-degree swing arc
    if direction == "NE":
        msp.add_line((ox + x, oy + y), (ox + x, oy + y + w), dxfattribs={"layer": "05_DOORS"})
        msp.add_arc((ox + x, oy + y), w, 0, 90, dxfattribs={"layer": "05_DOORS"})
    elif direction == "SE":
        msp.add_line((ox + x, oy + y), (ox + x, oy + y - w), dxfattribs={"layer": "05_DOORS"})
        msp.add_arc((ox + x, oy + y), w, 270, 360, dxfattribs={"layer": "05_DOORS"})
    elif direction == "NW":
        msp.add_line((ox + x, oy + y), (ox + x - w, oy + y), dxfattribs={"layer": "05_DOORS"})
        msp.add_arc((ox + x, oy + y), w, 90, 180, dxfattribs={"layer": "05_DOORS"})
    else:
        msp.add_line((ox + x, oy + y), (ox + x + w, oy + y), dxfattribs={"layer": "05_DOORS"})
        msp.add_arc((ox + x, oy + y), w, 0, 90, dxfattribs={"layer": "05_DOORS"})


def window(msp, ox, oy, x, y, w=1.60, horiz=True):
    if horiz:
        rect(msp, ox, oy, x, y - 0.08, w, 0.16, "06_WINDOWS")
        msp.add_line((ox + x, oy + y), (ox + x + w, oy + y), dxfattribs={"layer": "06_WINDOWS"})
    else:
        rect(msp, ox, oy, x - 0.08, y, 0.16, w, "06_WINDOWS")
        msp.add_line((ox + x, oy + y), (ox + x, oy + y + w), dxfattribs={"layer": "06_WINDOWS"})


# --- FURNITURE SYMBOLS ---
def furn_car(msp, ox, oy, x, y, w=1.85, l=4.20):
    cx, cy = x + (2.50 - w) / 2, y + (5.00 - l) / 2
    rect(msp, ox, oy, cx, cy, w, l, "12_FURNITURE")
    rect(msp, ox, oy, cx + 0.2, cy + 0.8, w - 0.4, l - 1.8, "12_FURNITURE")


def furn_bed(msp, ox, oy, x, y, w=1.60, l=2.00):
    rect(msp, ox, oy, x, y, w, l, "12_FURNITURE")
    rect(msp, ox, oy, x + 0.15, y + l - 0.45, 0.55, 0.35, "12_FURNITURE")
    rect(msp, ox, oy, x + w - 0.70, y + l - 0.45, 0.55, 0.35, "12_FURNITURE")


def furn_sofa(msp, ox, oy, x, y, w=2.20, d=0.85):
    rect(msp, ox, oy, x, y, w, d, "12_FURNITURE")
    rect(msp, ox, oy, x + 0.4, y + d + 0.35, 1.20, 0.60, "12_FURNITURE")  # coffee table


def furn_island_kitchen(msp, ox, oy, x, y):
    rect(msp, ox, oy, x, y, 2.80, 0.65, "12_FURNITURE")       # main counter
    rect(msp, ox, oy, x + 0.4, y + 1.40, 2.00, 0.90, "12_FURNITURE")  # island


def furn_bath(msp, ox, oy, x, y):
    rect(msp, ox, oy, x + 0.1, y + 0.1, 0.45, 0.65, "12_FURNITURE")  # WC
    rect(msp, ox, oy, x + 0.8, y + 0.1, 0.60, 0.45, "12_FURNITURE")  # sink


def draw_base_grid(msp, ox, oy, title, y_indices=range(len(GRID_Y))):
    rect(msp, ox, oy, 0, 0, LOT_W, LOT_L, "00_LOT")
    txt(msp, ox, oy, 0, LOT_L + 1.4, title, h=0.42, layer="11_TEXT")
    dim_h(msp, ox, oy, 0, LOT_W, -1.0, "12.50m")
    dim_v(msp, ox, oy, 0, LOT_L, -1.0, "30.00m")

    labels_x = ["A", "B", "C", "D"]
    for i, gx in enumerate(GRID_X):
        msp.add_line((ox + gx, oy - 0.5), (ox + gx, oy + LOT_L + 0.5), dxfattribs={"layer": "01_GRID"})
        txt(msp, ox, oy, gx - 0.1, LOT_L + 0.7, labels_x[i], h=0.25, layer="01_GRID")
        if i > 0:
            dim_h(msp, ox, oy, GRID_X[i - 1], gx, LOT_L + 0.35)

    for j, gy in enumerate(GRID_Y):
        msp.add_line((ox - 0.5, oy + gy), (ox + LOT_W + 0.5, oy + gy), dxfattribs={"layer": "01_GRID"})
        txt(msp, ox, oy, LOT_W + 0.6, gy - 0.1, str(j + 1), h=0.25, layer="01_GRID")
        if j > 0:
            dim_v(msp, ox, oy, GRID_Y[j - 1], gy, LOT_W + 0.35)

    for gx in GRID_X:
        for idx in y_indices:
            gy = GRID_Y[idx]
            rect(msp, ox, oy, gx - COL_SIZE / 2, gy - COL_SIZE / 2, COL_SIZE, COL_SIZE, "02_COLUMNS")


def draw_core(msp, ox, oy):
    ex, ey, ew, eh = ELEV_RECT
    rect(msp, ox, oy, ex, ey, ew, eh, "07_STAIRS_ELEV")
    msp.add_line((ox + ex, oy + ey), (ox + ex + ew, oy + ey + eh), dxfattribs={"layer": "07_STAIRS_ELEV"})
    msp.add_line((ox + ex, oy + ey + eh), (ox + ex + ew, oy + ey), dxfattribs={"layer": "07_STAIRS_ELEV"})
    txt(msp, ox, oy, ex + 0.2, ey + 0.9, "ELEV 8P", h=0.20, layer="07_STAIRS_ELEV")
    door(msp, ox, oy, ex + 0.45, ey, 0.90, "NE")

    sx, sy, sw, sh = STAIR_RECT
    rect(msp, ox, oy, sx, sy, sw, sh, "07_STAIRS_ELEV")
    for k in range(1, 11):
        ty = sy + k * (sh / 11.0)
        msp.add_line((ox + sx, oy + ty), (ox + sx + sw, oy + ty), dxfattribs={"layer": "07_STAIRS_ELEV"})
    msp.add_line((ox + sx + sw / 2, oy + sy), (ox + sx + sw / 2, oy + sy + sh), dxfattribs={"layer": "07_STAIRS_ELEV"})
    txt(msp, ox, oy, sx + 0.3, sy + 1.6, "STAIRCASE", h=0.20, layer="07_STAIRS_ELEV")
    # Staircase box door
    door(msp, ox, oy, sx + sw, sy + 0.4, 0.90, "NE")

    for idx, (dx, dy, dw, dh) in enumerate([DUCT_1, DUCT_2], 1):
        rect(msp, ox, oy, dx, dy, dw, dh, "09_MEP_DUCTS")
        txt(msp, ox, oy, dx + 0.1, dy + 0.4, f"D{idx}", h=0.18, layer="09_MEP_DUCTS")


def draw_lightwell(msp, ox, oy):
    px, py, pw, ph = PATIO_RECT
    rect(msp, ox, oy, px, py, pw, ph, "06_WINDOWS")
    msp.add_line((ox + px, oy + py), (ox + px + pw, oy + py + ph), dxfattribs={"layer": "06_WINDOWS"})
    msp.add_line((ox + px, oy + py + ph), (ox + px + pw, oy + py), dxfattribs={"layer": "06_WINDOWS"})
    txt(msp, ox, oy, px + 0.4, py + 1.6, "LIGHTWELL 3.6x3.4m", h=0.20, layer="06_WINDOWS")
    window(msp, ox, oy, px + 0.8, py, 1.60, horiz=True)
    window(msp, ox, oy, px + 0.8, py + ph, 1.60, horiz=True)


def draw_basement(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL -1: BASEMENT (H=2.60m)")
    wall_box(msp, ox, oy, 0.15, 0.15, LOT_W - 0.30, LOT_L - 0.30, t=0.20, layer="03_WALLS_EXT")

    rx, ry, rw, rh = RAMP_RECT
    rect(msp, ox, oy, rx, ry, rw, rh, "08_PARKING_RAMP")
    txt(msp, ox, oy, rx + 0.3, ry + 10.0, "RAMP 15% (3.5x20m) dH<=60cm", h=0.20, layer="08_PARKING_RAMP")

    for px, py, lbl in [(7.25, 24.50, "P1"), (9.75, 24.50, "P2"), (7.25, 11.75, "P3"), (9.75, 11.75, "P4")]:
        rect(msp, ox, oy, px, py, 2.50, 5.00, "08_PARKING_RAMP")
        furn_car(msp, ox, oy, px, py)
        txt(msp, ox, oy, px + 0.4, py + 2.4, f"{lbl}", h=0.22, layer="08_PARKING_RAMP")

    wall_box(msp, ox, oy, 7.25, 0.40, 4.90, 4.80, t=0.15)
    txt(msp, ox, oy, 7.60, 2.60, "MECH & PUMP ROOM", h=0.22)
    door(msp, ox, oy, 7.25, 3.80, 0.90, "NW")

    for i in range(4):
        sx = 4.25 + i * 2.00
        wall_box(msp, ox, oy, sx, 5.75, 1.95, 2.40, t=0.10)
        door(msp, ox, oy, sx + 0.5, 8.15, 0.75, "NE")
        txt(msp, ox, oy, sx + 0.2, 6.8, f"S{i+1}", h=0.18)
        wall_box(msp, ox, oy, sx, 8.25, 1.95, 2.40, t=0.10)
        door(msp, ox, oy, sx + 0.5, 10.65, 0.75, "NE")
        txt(msp, ox, oy, sx + 0.2, 9.3, f"S{i+5}", h=0.18)

    draw_core(msp, ox, oy)


def draw_ground(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 00: GROUND FLOOR")
    # Street Gates (Parking + Pedestrian)
    rect(msp, ox, oy, 0.25, 0.0, 3.50, 0.20, "05_DOORS")
    txt(msp, ox, oy, 0.4, -0.45, "PARKING GATE (RAMP)", h=0.18, layer="05_DOORS")
    rect(msp, ox, oy, 4.25, 0.0, 3.20, 0.20, "05_DOORS")
    txt(msp, ox, oy, 4.3, -0.45, "PARKING GATE (GROUND)", h=0.18, layer="05_DOORS")
    door(msp, ox, oy, 8.25, 0.0, 1.20, "NE")
    txt(msp, ox, oy, 8.2, -0.45, "PEDESTRIAN ENTRANCE", h=0.18, layer="05_DOORS")

    rx, ry, rw, rh = RAMP_RECT
    rect(msp, ox, oy, rx, ry, rw, rh, "08_PARKING_RAMP")
    txt(msp, ox, oy, rx + 0.3, ry + 5.0, "RAMP TO B-1 (15%) dH<=60cm", h=0.20, layer="08_PARKING_RAMP")

    for px, py, lbl in [(4.30, 0.50, "P5"), (6.90, 0.50, "P6"), (9.50, 0.50, "P7"), (9.50, 6.20, "P8")]:
        rect(msp, ox, oy, px, py, 2.50, 5.00, "08_PARKING_RAMP")
        furn_car(msp, ox, oy, px, py)
        txt(msp, ox, oy, px + 0.4, py + 2.4, f"{lbl}", h=0.22, layer="08_PARKING_RAMP")

    wall_box(msp, ox, oy, 4.25, 11.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.5, "MAIN LOBBY", h=0.22)
    door(msp, ox, oy, 5.65, 11.75, 1.20, "NE")

    wall_box(msp, ox, oy, 0.25, 21.50, 4.00, 8.25, t=0.15)
    txt(msp, ox, oy, 0.6, 25.5, "JANITOR LIVING/KITCHEN", h=0.20)
    furn_sofa(msp, ox, oy, 1.0, 23.0)
    door(msp, ox, oy, 4.25, 22.5, 0.90, "NW")
    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "JANITOR BEDROOM", h=0.20)
    furn_bed(msp, ox, oy, 9.5, 26.5)
    door(msp, ox, oy, 8.25, 24.5, 0.85, "NE")
    window(msp, ox, oy, 1.5, 29.75, 1.8, horiz=True)
    window(msp, ox, oy, 9.5, 29.75, 1.8, horiz=True)

    draw_lightwell(msp, ox, oy)
    draw_core(msp, ox, oy)


def draw_first(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 01: FIRST FLOOR (2-BED + 1-BED)", y_indices=[2, 3, 4, 5])
    # Unit 1 (South)
    wall_box(msp, ox, oy, 0.25, 11.75, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.6, "TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 13.75, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.6, "U1: ISLAND KITCHEN", h=0.20)
    furn_island_kitchen(msp, ox, oy, 0.8, 14.2)
    door(msp, ox, oy, 2.0, 13.75, 0.90, "SE")

    wall_box(msp, ox, oy, 4.25, 11.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.6, "U1: LIVING", h=0.20)
    furn_sofa(msp, ox, oy, 5.0, 12.8)
    door(msp, ox, oy, 6.0, 17.75, 0.90, "SE")
    window(msp, ox, oy, 5.2, 11.75, 2.2, horiz=True)

    wall_box(msp, ox, oy, 8.25, 11.75, 4.00, 3.50, t=0.15)
    txt(msp, ox, oy, 8.6, 13.4, "U1: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 9.8, 12.2)
    door(msp, ox, oy, 8.25, 13.0, 0.85, "NE")
    window(msp, ox, oy, 9.2, 11.75, 1.8, horiz=True)

    wall_box(msp, ox, oy, 8.25, 15.25, 4.00, 2.75, t=0.15)
    txt(msp, ox, oy, 8.6, 16.5, "U1: BED 2 + BATH", h=0.20)
    furn_bath(msp, ox, oy, 10.2, 15.5)
    door(msp, ox, oy, 8.25, 16.0, 0.80, "NE")

    # Unit 2 (North)
    wall_box(msp, ox, oy, 0.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "U2: LIVING + KITCHEN", h=0.20)
    furn_sofa(msp, ox, oy, 1.0, 25.0)
    door(msp, ox, oy, 4.25, 24.5, 0.90, "NW")
    wall_box(msp, ox, oy, 4.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "U2: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 5.5, 26.5)
    door(msp, ox, oy, 4.25, 27.0, 0.85, "NE")
    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "U2: TERRACE + STUDY", h=0.20)
    door(msp, ox, oy, 8.25, 26.0, 0.85, "NE")
    window(msp, ox, oy, 1.2, 29.75, 2.0, horiz=True)
    window(msp, ox, oy, 5.2, 29.75, 2.0, horiz=True)

    draw_lightwell(msp, ox, oy)
    draw_core(msp, ox, oy)


def draw_second(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 02: SECOND FLOOR (4-BED LUXURY)", y_indices=[2, 3, 4, 5])
    wall_box(msp, ox, oy, 0.25, 11.75, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.6, "SOUTH TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 13.75, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.6, "ISLAND KITCHEN", h=0.20)
    furn_island_kitchen(msp, ox, oy, 0.8, 14.2)
    door(msp, ox, oy, 2.0, 13.75, 0.90, "SE")

    wall_box(msp, ox, oy, 4.25, 11.75, 8.00, 6.00, t=0.15)
    txt(msp, ox, oy, 5.5, 14.6, "GRAND LIVING 48m2", h=0.24)
    furn_sofa(msp, ox, oy, 6.5, 13.0)
    door(msp, ox, oy, 6.0, 17.75, 1.00, "SE")
    window(msp, ox, oy, 5.5, 11.75, 3.0, horiz=True)

    wall_box(msp, ox, oy, 0.25, 17.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 20.5, "MASTER SUITE", h=0.20)
    furn_bed(msp, ox, oy, 1.5, 20.0)
    door(msp, ox, oy, 4.25, 19.0, 0.90, "NW")

    wall_box(msp, ox, oy, 0.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "BEDROOM 2", h=0.20)
    furn_bed(msp, ox, oy, 1.5, 26.5)
    door(msp, ox, oy, 2.0, 23.75, 0.85, "NE")

    wall_box(msp, ox, oy, 4.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "BEDROOM 3 + BATH", h=0.20)
    furn_bed(msp, ox, oy, 5.5, 26.5)
    door(msp, ox, oy, 6.0, 23.75, 0.85, "NE")

    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "BEDROOM 4", h=0.20)
    furn_bed(msp, ox, oy, 9.5, 26.5)
    door(msp, ox, oy, 8.25, 25.0, 0.85, "NE")

    window(msp, ox, oy, 1.2, 29.75, 2.0, horiz=True)
    window(msp, ox, oy, 5.2, 29.75, 2.0, horiz=True)
    window(msp, ox, oy, 9.2, 29.75, 2.0, horiz=True)

    draw_lightwell(msp, ox, oy)
    draw_core(msp, ox, oy)


def draw_typical_two(msp, ox=0, oy=0, title="LEVEL 03: THIRD FLOOR"):
    draw_base_grid(msp, ox, oy, title, y_indices=[2, 3, 4, 5])
    wall_box(msp, ox, oy, 0.25, 11.75, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.6, "TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 13.75, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.6, "SOUTH: ISLAND KITCHEN", h=0.20)
    furn_island_kitchen(msp, ox, oy, 0.8, 14.2)
    door(msp, ox, oy, 2.0, 13.75, 0.90, "SE")

    wall_box(msp, ox, oy, 4.25, 11.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.6, "SOUTH: LIVING", h=0.20)
    furn_sofa(msp, ox, oy, 5.0, 12.8)
    door(msp, ox, oy, 6.0, 17.75, 0.90, "SE")
    window(msp, ox, oy, 5.2, 11.75, 2.2, horiz=True)

    wall_box(msp, ox, oy, 8.25, 11.75, 4.00, 3.50, t=0.15)
    txt(msp, ox, oy, 8.6, 13.4, "SOUTH: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 9.8, 12.2)
    door(msp, ox, oy, 8.25, 13.0, 0.85, "NE")
    window(msp, ox, oy, 9.2, 11.75, 1.8, horiz=True)

    wall_box(msp, ox, oy, 8.25, 15.25, 4.00, 2.75, t=0.15)
    txt(msp, ox, oy, 8.6, 16.5, "SOUTH: BED 2 + BATH", h=0.20)
    furn_bath(msp, ox, oy, 10.2, 15.5)
    door(msp, ox, oy, 8.25, 16.0, 0.80, "NE")

    wall_box(msp, ox, oy, 0.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "NORTH: LIVING + KITCHEN", h=0.20)
    furn_sofa(msp, ox, oy, 1.0, 25.0)
    door(msp, ox, oy, 4.25, 24.5, 0.90, "NW")
    wall_box(msp, ox, oy, 4.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "NORTH: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 5.5, 26.5)
    door(msp, ox, oy, 4.25, 27.0, 0.85, "NE")
    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "NORTH: BED 2 + LAUNDRY", h=0.20)
    furn_bed(msp, ox, oy, 9.5, 26.5)
    door(msp, ox, oy, 8.25, 26.0, 0.85, "NE")
    window(msp, ox, oy, 1.2, 29.75, 2.0, horiz=True)
    window(msp, ox, oy, 5.2, 29.75, 2.0, horiz=True)
    window(msp, ox, oy, 9.2, 29.75, 2.0, horiz=True)

    draw_lightwell(msp, ox, oy)
    draw_core(msp, ox, oy)


builders = [
    ("output/dxf/01_basement.dxf", draw_basement),
    ("output/dxf/02_ground.dxf", draw_ground),
    ("output/dxf/03_first_floor.dxf", draw_first),
    ("output/dxf/04_second_floor.dxf", draw_second),
    ("output/dxf/05_third_floor.dxf", lambda msp, ox=0, oy=0: draw_typical_two(msp, ox, oy, "LEVEL 03: THIRD FLOOR (2x 2-BED)")),
    ("output/dxf/06_fourth_floor.dxf", lambda msp, ox=0, oy=0: draw_typical_two(msp, ox, oy, "LEVEL 04: FOURTH FLOOR (2x 2-BED)")),
]

for path, fn in builders:
    d = setup_doc()
    fn(d.modelspace(), 0, 0)
    d.saveas(path)

combined = setup_doc()
cmsp = combined.modelspace()
for idx, (_, fn) in enumerate(builders):
    fn(cmsp, idx * 20.0, 0)
combined.saveas("output/dxf/ALL_PLANS_COMBINED.dxf")

print("Detailed AutoCAD DXF plans generated.")
