import FreeCAD as App
import Part
import math

doc = App.ActiveDocument

# Create top-level part
main_part = doc.addObject("App::Part", "StudWallComplete")
main_part.Label = "Stud Wall Complete"

# Create sub-parts
frame_part = doc.addObject("App::Part", "Frame")
wrap_part = doc.addObject("App::Part", "WallWrap")
battens_part = doc.addObject("App::Part", "BattenSystem")
cladding_part = doc.addObject("App::Part", "Cladding")

# Group under main part
main_part.addObject(frame_part)
main_part.addObject(wrap_part)
main_part.addObject(battens_part)
main_part.addObject(cladding_part)

# Wall dimensions (mm)
wall_length = 2400
wall_height = 2700

# Studs
stud_spacing = 600
stud_width = 45
stud_depth = 90
plate_thickness = stud_width

# Wall wrap
wrap_thickness = 1

# Battens
batten_thickness = 20
batten_width = 45
batten_spacing = 600  # horizontal spacing between vertical battens

# Stud height
stud_height = wall_height - (2 * plate_thickness)

# Helper to create and parent a box
def create_box(container, name, x, y, z, x_offset=0, y_offset=0, z_offset=0):
    box = doc.addObject("Part::Box", name)
    box.Length = x
    box.Width = y
    box.Height = z
    box.Placement.Base = App.Vector(x_offset, y_offset, z_offset)
    container.addObject(box)
    return box

# --- Frame (Studs + Plates) ---
# Bottom plate
create_box(frame_part, "BottomPlate", wall_length, stud_depth, plate_thickness, 0, 0, 0)

# Top plate
create_box(frame_part, "TopPlate", wall_length, stud_depth, plate_thickness, 0, 0, wall_height - plate_thickness)

# Studs
num_studs = int(wall_length // stud_spacing) + 1

for i in range(num_studs):
    if i == num_studs - 1:
        x_offset = wall_length - stud_width
        create_box(
            frame_part,
            f"Stud_{i+1}",
            stud_width,
            stud_depth,
            stud_height,
            x_offset,
            0,
            plate_thickness
        )
    else:
        x_offset = i * stud_spacing
        create_box(
            frame_part,
            f"Stud_{i+1}",
            stud_width,
            stud_depth,
            stud_height,
            x_offset,
            0,
            plate_thickness
        )

# num_studs = int(wall_length // stud_spacing) + 1
# for i in range(num_studs):
#     x_offset = i * stud_spacing
#     create_box(frame_part, f"Stud_{i+1}", stud_width, stud_depth, stud_height, x_offset, 0, plate_thickness)

# --- Wall Wrap ---
create_box(wrap_part, "WallWrap", wall_length, wrap_thickness, wall_height, 0, stud_depth, 0)

# --- Battens (Vertical) ---
num_battens = int(wall_length // batten_spacing) + 1
for i in range(num_battens):
    if i == num_battens - 1:
        x_offset = wall_length - batten_width
        create_box(
            battens_part,
            f"Batten_{i+1}",
            batten_width,
            batten_thickness,
            wall_height,
            x_offset,
            stud_depth + wrap_thickness,
            0
        )
    else:
        x_offset = i * batten_spacing
        create_box(
            battens_part,
            f"Batten_{i+1}",
            batten_width,
            batten_thickness,
            wall_height,
            x_offset,
            stud_depth + wrap_thickness,
            0
        )

# --- Cladding (Tapered + Angled Weatherboards) ---
clad_y_offset = stud_depth + wrap_thickness + batten_thickness

# Geometry
top_thickness = 6
bottom_thickness = 22
board_height = 175
max_visible_height = 152

num_boards = int(wall_height // max_visible_height) + 1
visible_height = wall_height / num_boards

difference = bottom_thickness - top_thickness
difference_ratio = difference - (difference / board_height * visible_height)

weatherboard_y_offset = (top_thickness / (visible_height / board_height)) + difference_ratio
board_angle_rad = math.atan(weatherboard_y_offset / board_height)
board_angle_deg = math.degrees(board_angle_rad)  # ≈2.86°

for i in range(num_boards):
    z_base = i * visible_height

    # Trims last weatherboard to match the visible_height of the other weatherboards
    if i == num_boards - 1:
        actual_height = visible_height
        height_ratio = actual_height / board_height
        top_t = top_thickness * height_ratio
        bottom_t = bottom_thickness * height_ratio
    else:
        actual_height = board_height
        top_t = top_thickness
        bottom_t = bottom_thickness

    # Create trapezoid profile in XZ plane at origin
    p1 = App.Vector(0, 0, 0)                             # Bottom back
    p2 = App.Vector(0, 0, actual_height)                  # Top back
    p3 = App.Vector(0, bottom_t, 0)              # Bottom front
    p4 = App.Vector(0, top_t, actual_height)      # Top front

    wire = Part.makePolygon([p1, p2, p4, p3, p1])
    face = Part.Face(wire)

    # Extrude along wall (Y-axis)
    solid = face.extrude(App.Vector(wall_length, 0, 0))

    # Create object and attach to part container
    board = doc.addObject("Part::Feature", f"Weatherboard_{i+1}")
    board.Shape = solid
    cladding_part.addObject(board)

    # Placement
    placement = App.Placement()
    placement.Base = App.Vector(0, clad_y_offset + weatherboard_y_offset, z_base)
    placement.Rotation = App.Rotation(App.Vector(1, 0, 0), board_angle_deg)
    board.Placement = placement

# --- Spreadsheet for Material Takeoff ---
spreadsheet = doc.addObject("Spreadsheet::Sheet", "MaterialTakeoff")
doc.recompute()

def write_cell(value, row, col):
    spreadsheet.set(f"{col}{row}", str(value))

row = 1
write_cell("Component", row, "A")
write_cell("Count", row, "B")
write_cell("Unit Length (mm)", row, "C")
write_cell("Total Length (m)", row, "D")
row += 1

# --- Plates (top + bottom) ---
plate_count = 2
plate_unit_mm = wall_length
plate_total_m = plate_count * plate_unit_mm / 1000
write_cell("Plates", row, "A")
write_cell(plate_count, row, "B")
write_cell(f"{plate_unit_mm:.0f}", row, "C")
write_cell(f"{plate_total_m:.2f}", row, "D")
row += 1

# --- Studs ---
stud_count = num_studs
stud_unit_mm = stud_height
stud_total_m = stud_count * stud_unit_mm / 1000
write_cell("Studs", row, "A")
write_cell(stud_count, row, "B")
write_cell(f"{stud_unit_mm:.0f}", row, "C")
write_cell(f"{stud_total_m:.2f}", row, "D")
row += 1

# --- Battens ---
batten_count = num_battens
batten_unit_mm = wall_height
batten_total_m = batten_count * batten_unit_mm / 1000
write_cell("Battens", row, "A")
write_cell(batten_count, row, "B")
write_cell(f"{batten_unit_mm:.0f}", row, "C")
write_cell(f"{batten_total_m:.2f}", row, "D")
row += 1

# --- Weatherboards ---
board_count = num_boards
board_unit_mm = wall_length
board_total_m = board_count * board_unit_mm / 1000
write_cell("Weatherboards", row, "A")
write_cell(board_count, row, "B")
write_cell(f"{board_unit_mm:.0f}", row, "C")
write_cell(f"{board_total_m:.2f}", row, "D")
row += 1

doc.recompute()

