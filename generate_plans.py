import os
import ezdxf

os.makedirs("output/dxf", exist_ok=True)

LOT_W = 12.50
LOT_L = 30.00
GRID_X = [0.25, 4.25, 8.25, 12.25]
# 60% occupancy = 18.00 m (Y = 12.00 to 30.00)
GRID_Y = [0.25, 6.00, 12.00, 18.00, 24.00, 29.75]
COL_SIZE = 0.40

ELEV_RECT = (4.45, 18.00, 1.80, 2.00)
STAIR_RECT = (4.45, 20.00, 2.60, 4.00)
DUCT_1 = (7.25, 18.00, 0.80, 1.00)
DUCT_2 = (7.25, 22.80, 0.80, 1.00)
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


def door(msp, ox, oy, x, y, w=0.90, direction="NE", label=None):
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
    if label:
        txt(msp, ox, oy, x + 0.1, y + 0.1, label, h=0.16, layer="05_DOORS")


def window(msp, ox, oy, x, y, w=1.60, horiz=True):
    if horiz:
        rect(msp, ox, oy, x, y - 0.08, w, 0.16, "06_WINDOWS")
        msp.add_line((ox + x, oy + y), (ox + x + w, oy + y), dxfattribs={"layer": "06_WINDOWS"})
    else:
        rect(msp, ox, oy, x - 0.08, y, 0.16, w, "06_WINDOWS")
        msp.add_line((ox + x, oy + y), (ox + x, oy + y + w), dxfattribs={"layer": "06_WINDOWS"})


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
    rect(msp, ox, oy, x + 0.4, y + d + 0.35, 1.20, 0.60, "12_FURNITURE")


def furn_island_kitchen(msp, ox, oy, x, y):
    rect(msp, ox, oy, x, y, 2.80, 0.65, "12_FURNITURE")
    rect(msp, ox, oy, x + 0.4, y + 1.40, 2.00, 0.90, "12_FURNITURE")


def furn_bath(msp, ox, oy, x, y):
    rect(msp, ox, oy, x + 0.1, y + 0.1, 0.45, 0.65, "12_FURNITURE")
    rect(msp, ox, oy, x + 0.8, y + 0.1, 0.60, 0.45, "12_FURNITURE")


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
    # Elevator
    ex, ey, ew, eh = ELEV_RECT
    wall_box(msp, ox, oy, ex, ey, ew, eh, t=0.15, layer="07_STAIRS_ELEV")
    msp.add_line((ox + ex, oy + ey), (ox + ex + ew, oy + ey + eh), dxfattribs={"layer": "07_STAIRS_ELEV"})
    msp.add_line((ox + ex, oy + ey + eh), (ox + ex + ew, oy + ey), dxfattribs={"layer": "07_STAIRS_ELEV"})
    txt(msp, ox, oy, ex + 0.2, ey + 0.9, "ELEV 8P", h=0.20, layer="07_STAIRS_ELEV")
    door(msp, ox, oy, ex + ew, ey + 0.5, 0.90, "NE", "ELEV DOOR")

    # Standard Enclosed Staircase Box with Entry Landing & Mid-Landing
    sx, sy, sw, sh = STAIR_RECT
    wall_box(msp, ox, oy, sx, sy, sw, sh, t=0.20, layer="07_STAIRS_ELEV")
    # Entry Landing (y = 20.20 to 21.30)
    msp.add_line((ox + sx + 0.20, oy + sy + 1.20), (ox + sx + sw - 0.20, oy + sy + 1.20), dxfattribs={"layer": "07_STAIRS_ELEV"})
    txt(msp, ox, oy, sx + 0.5, sy + 0.6, "LANDING", h=0.16, layer="07_STAIRS_ELEV")
    # Mid-Landing (y = 23.00 to 23.80)
    msp.add_line((ox + sx + 0.20, oy + sy + sh - 1.00), (ox + sx + sw - 0.20, oy + sy + sh - 1.00), dxfattribs={"layer": "07_STAIRS_ELEV"})
    txt(msp, ox, oy, sx + 0.5, sy + sh - 0.6, "MID-LANDING", h=0.15, layer="07_STAIRS_ELEV")
    # Treads between landings
    for k in range(1, 7):
        ty = sy + 1.20 + k * ((sh - 2.20) / 7.0)
        msp.add_line((ox + sx + 0.20, oy + ty), (ox + sx + sw - 0.20, oy + ty), dxfattribs={"layer": "07_STAIRS_ELEV"})
    msp.add_line((ox + sx + sw / 2, oy + sy + 1.20), (ox + sx + sw / 2, oy + sy + sh - 1.00), dxfattribs={"layer": "07_STAIRS_ELEV"})
    door(msp, ox, oy, sx + sw, sy + 0.3, 0.90, "NE", "STAIR DOOR")

    txt(msp, ox, oy, 7.15, 20.5, "CORE LOBBY", h=0.18, layer="11_TEXT")

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

    # 4 Independent Parking Bays (zero blocking, 7.50m aisle)
    for px, py, lbl in [(7.25, 24.50, "P1"), (9.75, 24.50, "P2"), (7.25, 12.00, "P3"), (9.75, 12.00, "P4")]:
        rect(msp, ox, oy, px, py, 2.50, 5.00, "08_PARKING_RAMP")
        furn_car(msp, ox, oy, px, py)
        txt(msp, ox, oy, px + 0.4, py + 2.4, f"{lbl}", h=0.22, layer="08_PARKING_RAMP")

    wall_box(msp, ox, oy, 7.25, 0.40, 4.90, 4.80, t=0.15)
    txt(msp, ox, oy, 7.60, 2.60, "MECH & PUMP ROOM", h=0.22)
    door(msp, ox, oy, 7.25, 3.80, 0.90, "NW")

    # 8 Storage rooms starting at X=5.00 (1.25m clear passage from Ramp at X=3.75) + 1.40m central corridor
    for i in range(4):
        sx = 5.00 + i * 1.80
        wall_box(msp, ox, oy, sx, 5.40, 1.75, 1.90, t=0.10)
        door(msp, ox, oy, sx + 0.4, 7.30, 0.75, "NE")
        txt(msp, ox, oy, sx + 0.2, 6.2, f"S{i+1}", h=0.18)

        wall_box(msp, ox, oy, sx, 8.70, 1.75, 1.90, t=0.10)
        door(msp, ox, oy, sx + 0.4, 8.70, 0.75, "SE")
        txt(msp, ox, oy, sx + 0.2, 9.5, f"S{i+5}", h=0.18)

    txt(msp, ox, oy, 5.5, 7.9, "STORAGE CORRIDOR (1.40m)", h=0.18, layer="11_TEXT")
    dim_h(msp, ox, oy, 3.75, 5.00, 6.50, "1.25m")
    draw_core(msp, ox, oy)


def draw_ground(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 00: GROUND FLOOR (4 INDEPENDENT PARKING + LOBBY)")
    # Street Gates (Parking + Pedestrian)
    rect(msp, ox, oy, 0.25, 0.0, 3.50, 0.20, "05_DOORS")
    txt(msp, ox, oy, 0.4, -0.45, "RAMP GATE (IN/OUT)", h=0.18, layer="05_DOORS")
    rect(msp, ox, oy, 4.25, 0.0, 3.50, 0.20, "05_DOORS")
    txt(msp, ox, oy, 4.3, -0.45, "GROUND PARKING GATE", h=0.18, layer="05_DOORS")
    door(msp, ox, oy, 8.50, 0.0, 1.20, "NE", "BUILDING ENTRANCE")

    rx, ry, rw, rh = RAMP_RECT
    rect(msp, ox, oy, rx, ry, rw, rh, "08_PARKING_RAMP")
    txt(msp, ox, oy, rx + 0.3, ry + 5.0, "RAMP TO B-1 (15%) dH<=60cm", h=0.20, layer="08_PARKING_RAMP")

    # 4 Independent Parking Bays at Y=6.00..11.00 with 5.80m drive aisle (Y=0.20..6.00) -> ZERO BLOCKING
    for idx, lbl in enumerate(["P5", "P6", "P7", "P8"]):
        px = 4.25 + idx * 2.00
        # 2.00m? No, 2.50m x 5.00m: 3 bays at Y=6.00 (X=4.50, 7.00, 9.50) + 1 bay at X=9.50, Y=0.50
    for px, py, lbl in [(4.50, 6.20, "P5"), (7.00, 6.20, "P6"), (9.50, 6.20, "P7"), (9.50, 0.50, "P8")]:
        rect(msp, ox, oy, px, py, 2.50, 5.00, "08_PARKING_RAMP")
        furn_car(msp, ox, oy, px, py)
        txt(msp, ox, oy, px + 0.4, py + 2.4, f"{lbl}", h=0.22, layer="08_PARKING_RAMP")

    txt(msp, ox, oy, 5.0, 3.0, "DRIVE AISLE (5.50m) ->", h=0.20, layer="08_PARKING_RAMP")

    wall_box(msp, ox, oy, 4.25, 12.00, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.5, "MAIN LOBBY", h=0.22)
    door(msp, ox, oy, 5.65, 12.00, 1.20, "NE", "LOBBY DOOR")

    wall_box(msp, ox, oy, 0.25, 21.50, 4.00, 8.25, t=0.15)
    txt(msp, ox, oy, 0.6, 25.5, "JANITOR LIVING/KITCHEN", h=0.20)
    furn_sofa(msp, ox, oy, 1.0, 23.0)
    door(msp, ox, oy, 4.25, 22.5, 0.90, "NW", "JANITOR ENTRANCE")
    wall_box(msp, ox, oy, 8.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "JANITOR BEDROOM", h=0.20)
    furn_bed(msp, ox, oy, 9.5, 26.5)
    door(msp, ox, oy, 8.25, 24.5, 0.85, "NE")
    window(msp, ox, oy, 1.5, 29.75, 1.8, horiz=True)
    window(msp, ox, oy, 9.5, 29.75, 1.8, horiz=True)

    draw_lightwell(msp, ox, oy)
    draw_core(msp, ox, oy)


def draw_first(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 01: FIRST FLOOR (60% = 18.0m)", y_indices=[2, 3, 4, 5])
    wall_box(msp, ox, oy, 0.25, 12.00, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.8, "TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 14.00, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.8, "U1: ISLAND KITCHEN", h=0.20)
    furn_island_kitchen(msp, ox, oy, 0.8, 14.4)
    door(msp, ox, oy, 2.0, 14.00, 0.90, "SE")

    wall_box(msp, ox, oy, 4.25, 12.00, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.8, "U1: LIVING", h=0.20)
    furn_sofa(msp, ox, oy, 5.0, 13.0)
    door(msp, ox, oy, 6.0, 18.00, 1.00, "SE", "U1 ENTRANCE")
    window(msp, ox, oy, 5.2, 12.00, 2.2, horiz=True)

    wall_box(msp, ox, oy, 8.25, 12.00, 4.00, 3.50, t=0.15)
    txt(msp, ox, oy, 8.6, 13.6, "U1: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 9.8, 12.4)
    door(msp, ox, oy, 8.25, 13.2, 0.85, "NE")
    window(msp, ox, oy, 9.2, 12.00, 1.8, horiz=True)

    wall_box(msp, ox, oy, 8.25, 15.50, 4.00, 2.50, t=0.15)
    txt(msp, ox, oy, 8.6, 16.6, "U1: BED 2 + BATH", h=0.20)
    furn_bath(msp, ox, oy, 10.2, 15.7)
    door(msp, ox, oy, 8.25, 16.2, 0.80, "NE")

    wall_box(msp, ox, oy, 0.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "U2: LIVING + KITCHEN", h=0.20)
    furn_sofa(msp, ox, oy, 1.0, 25.0)
    door(msp, ox, oy, 4.25, 24.00, 1.00, "NE", "U2 ENTRANCE")
    wall_box(msp, ox, oy, 4.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "U2: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 5.5, 26.5)
    door(msp, ox, oy, 4.25, 27.0, 0.85, "NE")
    wall_box(msp, ox, oy, 8.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "U2: TERRACE + STUDY", h=0.20)
    door(msp, ox, oy, 8.25, 26.0, 0.85, "NE")
    window(msp, ox, oy, 1.2, 29.75, 2.0, horiz=True)
    window(msp, ox, oy, 5.2, 29.75, 2.0, horiz=True)

    draw_lightwell(msp, ox, oy)
    draw_core(msp, ox, oy)


def draw_second(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 02: SECOND FLOOR (60% = 18.0m)", y_indices=[2, 3, 4, 5])
    wall_box(msp, ox, oy, 0.25, 12.00, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.8, "SOUTH TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 14.00, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.8, "ISLAND KITCHEN", h=0.20)
    furn_island_kitchen(msp, ox, oy, 0.8, 14.4)
    door(msp, ox, oy, 2.0, 14.00, 0.90, "SE")

    wall_box(msp, ox, oy, 4.25, 12.00, 8.00, 6.00, t=0.15)
    txt(msp, ox, oy, 5.5, 14.8, "GRAND LIVING 48m2", h=0.24)
    furn_sofa(msp, ox, oy, 6.5, 13.0)
    door(msp, ox, oy, 6.0, 18.00, 1.10, "SE", "U3 MAIN ENTRANCE")
    window(msp, ox, oy, 5.5, 12.00, 3.0, horiz=True)

    wall_box(msp, ox, oy, 0.25, 18.00, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 20.5, "MASTER SUITE", h=0.20)
    furn_bed(msp, ox, oy, 1.5, 20.0)
    door(msp, ox, oy, 4.25, 19.0, 0.90, "NW")

    wall_box(msp, ox, oy, 0.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "BEDROOM 2", h=0.20)
    furn_bed(msp, ox, oy, 1.5, 26.5)
    door(msp, ox, oy, 2.0, 24.00, 0.85, "NE")

    wall_box(msp, ox, oy, 4.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "BEDROOM 3 + BATH", h=0.20)
    furn_bed(msp, ox, oy, 5.5, 26.5)
    door(msp, ox, oy, 6.0, 24.00, 0.85, "NE")

    wall_box(msp, ox, oy, 8.25, 24.00, 4.00, 5.75, t=0.15)
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
    wall_box(msp, ox, oy, 0.25, 12.00, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.8, "TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 14.00, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.8, "SOUTH: ISLAND KITCHEN", h=0.20)
    furn_island_kitchen(msp, ox, oy, 0.8, 14.4)
    door(msp, ox, oy, 2.0, 14.00, 0.90, "SE")

    wall_box(msp, ox, oy, 4.25, 12.00, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.8, "SOUTH: LIVING", h=0.20)
    furn_sofa(msp, ox, oy, 5.0, 13.0)
    door(msp, ox, oy, 6.0, 18.00, 1.00, "SE", "SOUTH UNIT ENTRANCE")
    window(msp, ox, oy, 5.2, 12.00, 2.2, horiz=True)

    wall_box(msp, ox, oy, 8.25, 12.00, 4.00, 3.50, t=0.15)
    txt(msp, ox, oy, 8.6, 13.6, "SOUTH: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 9.8, 12.4)
    door(msp, ox, oy, 8.25, 13.2, 0.85, "NE")
    window(msp, ox, oy, 9.2, 12.00, 1.8, horiz=True)

    wall_box(msp, ox, oy, 8.25, 15.50, 4.00, 2.50, t=0.15)
    txt(msp, ox, oy, 8.6, 16.6, "SOUTH: BED 2 + BATH", h=0.20)
    furn_bath(msp, ox, oy, 10.2, 15.7)
    door(msp, ox, oy, 8.25, 16.2, 0.80, "NE")

    wall_box(msp, ox, oy, 0.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "NORTH: LIVING + KITCHEN", h=0.20)
    furn_sofa(msp, ox, oy, 1.0, 25.0)
    door(msp, ox, oy, 4.25, 24.00, 1.00, "NE", "NORTH UNIT ENTRANCE")
    wall_box(msp, ox, oy, 4.25, 24.00, 4.00, 5.75, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "NORTH: MASTER BED", h=0.20)
    furn_bed(msp, ox, oy, 5.5, 26.5)
    door(msp, ox, oy, 4.25, 27.0, 0.85, "NE")
    wall_box(msp, ox, oy, 8.25, 24.00, 4.00, 5.75, t=0.15)
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
    ("output/dxf/05_third_floor.dxf", lambda msp, ox=0, oy=0: draw_typical_two(msp, ox, oy, "LEVEL 03: THIRD FLOOR (60% = 18.0m)")),
    ("output/dxf/06_fourth_floor.dxf", lambda msp, ox=0, oy=0: draw_typical_two(msp, ox, oy, "LEVEL 04: FOURTH FLOOR (60% = 18.0m)")),
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

print("Updated DXF plans with 60% occupancy, 1.25m ramp-to-storage clearance, zero-blocking parking, and stair landings.")
