import FreeCAD as App
import Sketcher
import math

doc = App.ActiveDocument

# Create new sketch in XZ plane (normal to Y axis)
sketch = doc.addObject('Sketcher::SketchObject', 'WeatherboardProfile')
sketch.Placement = App.Placement(
    App.Vector(0, 0, 0),
    App.Rotation(App.Vector(0, 1, 0), 90)  # Face normal = Y+
)

# Parameters
board_height = 180
top_thickness = 10
bullnose_radius = 8

# --- Add Geometry ---
# Back edge
back_line = sketch.addGeometry(Part.LineSegment(App.Vector(0, 0), App.Vector(0, board_height)))

# Top edge
top_line = sketch.addGeometry(Part.LineSegment(App.Vector(0, board_height), App.Vector(top_thickness, board_height)))

# Arc (bullnose) → draw counterclockwise from top edge to bottom
arc_start = App.Vector(top_thickness, board_height)
arc_end = App.Vector(top_thickness + 2 * bullnose_radius, board_height - 2 * bullnose_radius)
arc_center = App.Vector(top_thickness + bullnose_radius, board_height - bullnose_radius)

arc_index = sketch.addGeometry(Part.Arc(arc_start, arc_center, arc_end))

# Bottom edge
bottom_line = sketch.addGeometry(Part.LineSegment(arc_end, App.Vector(0, 0)))

# --- Constraints ---
# Lock bottom-left point to origin
sketch.addConstraint(Sketcher.Constraint('Lock', 0, 1, 0, 0))

# Coincidence between points
sketch.addConstraint(Sketcher.Constraint('Coincident', back_line, 2, top_line, 1))     # top of back to start of top
sketch.addConstraint(Sketcher.Constraint('Coincident', top_line, 2, arc_index, 1))     # end of top to arc start
sketch.addConstraint(Sketcher.Constraint('Coincident', arc_index, 2, bottom_line, 1))  # arc end to bottom start
sketch.addConstraint(Sketcher.Constraint('Coincident', bottom_line, 2, back_line, 1))  # end of bottom to bottom of back

# Horizontal top and bottom
sketch.addConstraint(Sketcher.Constraint('Horizontal', top_line))
sketch.addConstraint(Sketcher.Constraint('Horizontal', bottom_line))

# Vertical back
sketch.addConstraint(Sketcher.Constraint('Vertical', back_line))

# Dimensions
sketch.addConstraint(Sketcher.Constraint('DistanceY', back_line, 180))                # board height
sketch.addConstraint(Sketcher.Constraint('DistanceX', top_line, 10))                  # top thickness
sketch.addConstraint(Sketcher.Constraint('Radius', arc_index, bullnose_radius))       # bullnose radius

doc.recompute()
