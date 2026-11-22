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
        ("05_DOORS_WINDOWS", 3),
        ("06_STAIRS_ELEV", 4),
        ("07_PARKING_RAMP", 5),
        ("08_MEP_DUCTS", 6),
        ("09_DIMENSIONS", 2),
        ("10_TEXT", 2),
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


def txt(msp, ox, oy, x, y, s, h=0.22, layer="10_TEXT"):
    msp.add_text(s, dxfattribs={"height": h, "layer": layer}).set_placement((ox + x, oy + y))


def dim_h(msp, ox, oy, x1, x2, y, label=None):
    msp.add_line((ox + x1, oy + y), (ox + x2, oy + y), dxfattribs={"layer": "09_DIMENSIONS"})
    msp.add_line((ox + x1, oy + y - 0.15), (ox + x1, oy + y + 0.15), dxfattribs={"layer": "09_DIMENSIONS"})
    msp.add_line((ox + x2, oy + y - 0.15), (ox + x2, oy + y + 0.15), dxfattribs={"layer": "09_DIMENSIONS"})
    val = label if label else f"{abs(x2 - x1):.2f}m"
    txt(msp, ox, oy, (x1 + x2) / 2 - 0.4, y + 0.12, val, h=0.20, layer="09_DIMENSIONS")


def dim_v(msp, ox, oy, y1, y2, x, label=None):
    msp.add_line((ox + x, oy + y1), (ox + x, oy + y2), dxfattribs={"layer": "09_DIMENSIONS"})
    msp.add_line((ox + x - 0.15, oy + y1), (ox + x + 0.15, oy + y1), dxfattribs={"layer": "09_DIMENSIONS"})
    msp.add_line((ox + x - 0.15, oy + y2), (ox + x + 0.15, oy + y2), dxfattribs={"layer": "09_DIMENSIONS"})
    val = label if label else f"{abs(y2 - y1):.2f}m"
    txt(msp, ox, oy, x + 0.12, (y1 + y2) / 2, val, h=0.20, layer="09_DIMENSIONS")


def door(msp, ox, oy, x, y, w=0.90, horiz=True):
    if horiz:
        msp.add_line((ox + x, oy + y), (ox + x, oy + y + w), dxfattribs={"layer": "05_DOORS_WINDOWS"})
        msp.add_arc((ox + x, oy + y), w, 0, 90, dxfattribs={"layer": "05_DOORS_WINDOWS"})
    else:
        msp.add_line((ox + x, oy + y), (ox + x + w, oy + y), dxfattribs={"layer": "05_DOORS_WINDOWS"})
        msp.add_arc((ox + x, oy + y), w, 0, 90, dxfattribs={"layer": "05_DOORS_WINDOWS"})


def window(msp, ox, oy, x, y, w=1.60, horiz=True):
    if horiz:
        rect(msp, ox, oy, x, y - 0.05, w, 0.10, "05_DOORS_WINDOWS")
    else:
        rect(msp, ox, oy, x - 0.05, y, 0.10, w, "05_DOORS_WINDOWS")


def draw_base_grid(msp, ox, oy, title, y_indices=range(len(GRID_Y))):
    rect(msp, ox, oy, 0, 0, LOT_W, LOT_L, "00_LOT")
    txt(msp, ox, oy, 0, LOT_L + 1.4, title, h=0.45, layer="10_TEXT")

    # Overall dimensions
    dim_h(msp, ox, oy, 0, LOT_W, -1.0, "12.50m")
    dim_v(msp, ox, oy, 0, LOT_L, -1.0, "30.00m")

    labels_x = ["A", "B", "C", "D"]
    for i, gx in enumerate(GRID_X):
        msp.add_line((ox + gx, oy - 0.5), (ox + gx, oy + LOT_L + 0.5), dxfattribs={"layer": "01_GRID"})
        txt(msp, ox, oy, gx - 0.1, LOT_L + 0.7, labels_x[i], h=0.28, layer="01_GRID")
        if i > 0:
            dim_h(msp, ox, oy, GRID_X[i - 1], gx, LOT_L + 0.35)

    for j, gy in enumerate(GRID_Y):
        msp.add_line((ox - 0.5, oy + gy), (ox + LOT_W + 0.5, oy + gy), dxfattribs={"layer": "01_GRID"})
        txt(msp, ox, oy, LOT_W + 0.6, gy - 0.1, str(j + 1), h=0.28, layer="01_GRID")
        if j > 0:
            dim_v(msp, ox, oy, GRID_Y[j - 1], gy, LOT_W + 0.35)

    for gx in GRID_X:
        for idx in y_indices:
            gy = GRID_Y[idx]
            rect(msp, ox, oy, gx - COL_SIZE / 2, gy - COL_SIZE / 2, COL_SIZE, COL_SIZE, "02_COLUMNS")


def draw_core(msp, ox, oy):
    ex, ey, ew, eh = ELEV_RECT
    rect(msp, ox, oy, ex, ey, ew, eh, "06_STAIRS_ELEV")
    msp.add_line((ox + ex, oy + ey), (ox + ex + ew, oy + ey + eh), dxfattribs={"layer": "06_STAIRS_ELEV"})
    msp.add_line((ox + ex, oy + ey + eh), (ox + ex + ew, oy + ey), dxfattribs={"layer": "06_STAIRS_ELEV"})
    txt(msp, ox, oy, ex + 0.2, ey + 0.9, "ELEV 8P\n1.8x2.0m", h=0.20, layer="06_STAIRS_ELEV")

    sx, sy, sw, sh = STAIR_RECT
    rect(msp, ox, oy, sx, sy, sw, sh, "06_STAIRS_ELEV")
    for k in range(1, 11):
        ty = sy + k * (sh / 11.0)
        msp.add_line((ox + sx, oy + ty), (ox + sx + sw, oy + ty), dxfattribs={"layer": "06_STAIRS_ELEV"})
    msp.add_line((ox + sx + sw / 2, oy + sy), (ox + sx + sw / 2, oy + sy + sh), dxfattribs={"layer": "06_STAIRS_ELEV"})
    txt(msp, ox, oy, sx + 0.3, sy + 1.6, "STAIRS 2.6x3.55m", h=0.20, layer="06_STAIRS_ELEV")

    for idx, (dx, dy, dw, dh) in enumerate([DUCT_1, DUCT_2], 1):
        rect(msp, ox, oy, dx, dy, dw, dh, "08_MEP_DUCTS")
        txt(msp, ox, oy, dx + 0.1, dy + 0.4, f"D{idx}", h=0.18, layer="08_MEP_DUCTS")


def draw_basement(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL -1: BASEMENT (H=2.60m)")
    wall_box(msp, ox, oy, 0.15, 0.15, LOT_W - 0.30, LOT_L - 0.30, t=0.20, layer="03_WALLS_EXT")

    rx, ry, rw, rh = RAMP_RECT
    rect(msp, ox, oy, rx, ry, rw, rh, "07_PARKING_RAMP")
    txt(msp, ox, oy, rx + 0.3, ry + 10.0, "RAMP 15% (3.5x20m) dH<=60cm", h=0.22, layer="07_PARKING_RAMP")

    for i, (px, py, lbl) in enumerate([(7.25, 24.50, "P1"), (9.75, 24.50, "P2"), (7.25, 11.75, "P3"), (9.75, 11.75, "P4")]):
        rect(msp, ox, oy, px, py, 2.50, 5.00, "07_PARKING_RAMP")
        txt(msp, ox, oy, px + 0.4, py + 2.4, f"{lbl} 2.5x5.0m", h=0.22, layer="07_PARKING_RAMP")

    wall_box(msp, ox, oy, 7.25, 0.40, 4.90, 4.80, t=0.15)
    txt(msp, ox, oy, 7.60, 2.60, "MECH & PUMP ROOM 4.9x4.8m", h=0.22)
    door(msp, ox, oy, 7.25, 4.00, 0.90, horiz=False)

    for i in range(4):
        sx = 4.25 + i * 2.00
        wall_box(msp, ox, oy, sx, 5.75, 1.95, 2.40, t=0.10)
        txt(msp, ox, oy, sx + 0.2, 6.8, f"S{i+1} 2x2.4", h=0.16)
        wall_box(msp, ox, oy, sx, 8.25, 1.95, 2.40, t=0.10)
        txt(msp, ox, oy, sx + 0.2, 9.3, f"S{i+5} 2x2.4", h=0.16)

    draw_core(msp, ox, oy)


def draw_ground(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 00: GROUND FLOOR")
    rx, ry, rw, rh = RAMP_RECT
    rect(msp, ox, oy, rx, ry, rw, rh, "07_PARKING_RAMP")
    txt(msp, ox, oy, rx + 0.3, ry + 5.0, "RAMP TO B-1 (15%) dH<=60cm", h=0.22, layer="07_PARKING_RAMP")

    for px, py, lbl in [(4.30, 0.50, "P5"), (6.90, 0.50, "P6"), (9.50, 0.50, "P7"), (9.50, 6.20, "P8")]:
        rect(msp, ox, oy, px, py, 2.50, 5.00, "07_PARKING_RAMP")
        txt(msp, ox, oy, px + 0.4, py + 2.4, f"{lbl} 2.5x5.0m", h=0.22, layer="07_PARKING_RAMP")

    wall_box(msp, ox, oy, 4.25, 11.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.5, "MAIN LOBBY 4.0x6.0m", h=0.22)
    door(msp, ox, oy, 5.80, 11.75, 1.20, horiz=True)

    wall_box(msp, ox, oy, 0.25, 21.50, 4.00, 8.25, t=0.15)
    txt(msp, ox, oy, 0.6, 25.5, "JANITOR LIVING/KITCHEN", h=0.20)
    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "JANITOR BEDROOM", h=0.20)
    window(msp, ox, oy, 1.5, 29.75, 1.8, horiz=True)
    window(msp, ox, oy, 9.5, 29.75, 1.8, horiz=True)

    px, py, pw, ph = PATIO_RECT
    rect(msp, ox, oy, px, py, pw, ph, "05_DOORS_WINDOWS")
    txt(msp, ox, oy, px + 0.5, py + 1.6, "LIGHTWELL 3.6x3.4m", h=0.20)
    draw_core(msp, ox, oy)


def draw_first(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 01: FIRST FLOOR (2-BED + 1-BED)", y_indices=[2, 3, 4, 5])
    # Unit 1 (South)
    wall_box(msp, ox, oy, 0.25, 11.75, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.6, "TERRACE 4.0x2.0m", h=0.20)
    wall_box(msp, ox, oy, 0.25, 13.75, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.6, "U1: ISLAND KITCHEN 4x4m", h=0.20)
    wall_box(msp, ox, oy, 4.25, 11.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.6, "U1: LIVING 4.0x6.0m", h=0.20)
    window(msp, ox, oy, 5.2, 11.75, 2.2, horiz=True)
    wall_box(msp, ox, oy, 8.25, 11.75, 4.00, 3.50, t=0.15)
    txt(msp, ox, oy, 8.6, 13.4, "U1: MASTER BED 4x3.5m", h=0.20)
    window(msp, ox, oy, 9.2, 11.75, 1.8, horiz=True)
    wall_box(msp, ox, oy, 8.25, 15.25, 4.00, 2.75, t=0.15)
    txt(msp, ox, oy, 8.6, 16.5, "U1: BED 2 + BATH", h=0.20)

    # Unit 2 (North)
    wall_box(msp, ox, oy, 0.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "U2: LIVING + KITCHEN", h=0.20)
    wall_box(msp, ox, oy, 4.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "U2: MASTER BED 4x6m", h=0.20)
    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "U2: TERRACE + STUDY", h=0.20)
    window(msp, ox, oy, 1.2, 29.75, 2.0, horiz=True)
    window(msp, ox, oy, 5.2, 29.75, 2.0, horiz=True)

    px, py, pw, ph = PATIO_RECT
    rect(msp, ox, oy, px, py, pw, ph, "05_DOORS_WINDOWS")
    txt(msp, ox, oy, px + 0.5, py + 1.6, "LIGHTWELL 3.6x3.4m", h=0.20)
    draw_core(msp, ox, oy)


def draw_second(msp, ox=0, oy=0):
    draw_base_grid(msp, ox, oy, "LEVEL 02: SECOND FLOOR (4-BED LUXURY)", y_indices=[2, 3, 4, 5])
    wall_box(msp, ox, oy, 0.25, 11.75, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.6, "SOUTH TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 13.75, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.6, "ISLAND KITCHEN + LAUNDRY", h=0.20)
    wall_box(msp, ox, oy, 4.25, 11.75, 8.00, 6.00, t=0.15)
    txt(msp, ox, oy, 5.5, 14.6, "GRAND LIVING 8.0x6.0m (48m2)", h=0.24)
    window(msp, ox, oy, 5.5, 11.75, 3.0, horiz=True)

    wall_box(msp, ox, oy, 0.25, 17.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 20.5, "MASTER SUITE + WIC", h=0.20)
    wall_box(msp, ox, oy, 0.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "BEDROOM 2 (EN-SUITE)", h=0.20)
    wall_box(msp, ox, oy, 4.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "BEDROOM 3 + BATH", h=0.20)
    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "BEDROOM 4 + TERRACE", h=0.20)

    px, py, pw, ph = PATIO_RECT
    rect(msp, ox, oy, px, py, pw, ph, "05_DOORS_WINDOWS")
    txt(msp, ox, oy, px + 0.5, py + 1.6, "LIGHTWELL 3.6x3.4m", h=0.20)
    draw_core(msp, ox, oy)


def draw_typical_two(msp, ox=0, oy=0, title="LEVEL 03: THIRD FLOOR"):
    draw_base_grid(msp, ox, oy, title, y_indices=[2, 3, 4, 5])
    wall_box(msp, ox, oy, 0.25, 11.75, 4.00, 2.00, t=0.10)
    txt(msp, ox, oy, 0.6, 12.6, "TERRACE", h=0.20)
    wall_box(msp, ox, oy, 0.25, 13.75, 4.00, 4.00, t=0.15)
    txt(msp, ox, oy, 0.6, 15.6, "SOUTH: ISLAND KITCHEN", h=0.20)
    wall_box(msp, ox, oy, 4.25, 11.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 14.6, "SOUTH: LIVING 4x6m", h=0.20)
    wall_box(msp, ox, oy, 8.25, 11.75, 4.00, 3.50, t=0.15)
    txt(msp, ox, oy, 8.6, 13.4, "SOUTH: MASTER BED", h=0.20)
    wall_box(msp, ox, oy, 8.25, 15.25, 4.00, 2.75, t=0.15)
    txt(msp, ox, oy, 8.6, 16.5, "SOUTH: BED 2 + LAUNDRY", h=0.20)

    wall_box(msp, ox, oy, 0.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 0.6, 26.5, "NORTH: LIVING + KITCHEN", h=0.20)
    wall_box(msp, ox, oy, 4.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 4.6, 26.5, "NORTH: MASTER BED", h=0.20)
    wall_box(msp, ox, oy, 8.25, 23.75, 4.00, 6.00, t=0.15)
    txt(msp, ox, oy, 8.6, 26.5, "NORTH: BED 2 + LAUNDRY", h=0.20)

    px, py, pw, ph = PATIO_RECT
    rect(msp, ox, oy, px, py, pw, ph, "05_DOORS_WINDOWS")
    txt(msp, ox, oy, px + 0.5, py + 1.6, "LIGHTWELL 3.6x3.4m", h=0.20)
    draw_core(msp, ox, oy)


# Individual DXFs
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

# Combined DXF (all 6 plans side-by-side)
combined = setup_doc()
cmsp = combined.modelspace()
for idx, (_, fn) in enumerate(builders):
    fn(cmsp, idx * 20.0, 0)
combined.saveas("output/dxf/ALL_PLANS_COMBINED.dxf")

print("All DXF files generated successfully.")
