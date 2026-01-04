import FreeCAD as App
import Part


class WallAssembly:
    """Parametric 2D wall assembly (plan view)"""

    def __init__(self, obj):
        self.Type = "BuildQ::WallAssembly"
        obj.Proxy = self

        # ---- Core parameters ----
        obj.addProperty(
            "App::PropertyVector",
            "Start",
            "Geometry",
            "Wall start point"
        )

        obj.addProperty(
            "App::PropertyVector",
            "End",
            "Geometry",
            "Wall end point"
        )

        obj.addProperty(
            "App::PropertyLength",
            "Thickness",
            "Geometry",
            "Wall thickness"
        ).Thickness = 90

        obj.addProperty(
            "App::PropertyBool",
            "Show2DDetail",
            "Display",
            "Show 2D framing detail"
        ).Show2DDetail = True

    def execute(self, obj):
        """Recompute wall geometry"""
        p1 = obj.Start
        p2 = obj.End

        if p1 is None or p2 is None:
            return

        # Defensive thickness extraction: support both property objects and raw numbers
        try:
            thickness_val = getattr(obj.Thickness, 'Value', obj.Thickness)
        except Exception:
            thickness_val = obj.Thickness

        # (debug output removed)

        shape = self.makeWallShape(p1, p2, thickness_val)
        if shape is None:
            
            obj.Shape = Part.Shape()
        else:
            obj.Shape = shape
            

    # -------------------------
    # Geometry
    # -------------------------
    def makeWallShape(self, p1, p2, thickness):
        direction = p2.sub(p1)
        length = direction.Length
        if length == 0:
            return Part.Shape()

        direction.normalize()
        normal = App.Vector(-direction.y, direction.x, 0)
        offset = normal.multiply(thickness / 2)

        pts = [
            p1.add(offset),
            p2.add(offset),
            p2.sub(offset),
            p1.sub(offset),
            p1.add(offset),
        ]

        wire = Part.makePolygon(pts)
        try:
            face = Part.Face(wire)
            # return both face and wire as a compound so edges are available/visible
            try:
                comp = Part.makeCompound([face, wire])
                return comp
            except Exception:
                return face
        except Exception:
            return wire


class WallViewProvider:
    """Minimal view provider for WallAssembly so DisplayMode works."""
    def __init__(self, vobj=None):
        if vobj is not None:
            self.attach(vobj)

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        try:
            vobj.Proxy = self
        except Exception:
            try:
                vobj.Object.ViewObject.Proxy = self
            except Exception:
                pass

    def updateData(self, fp, prop):
        pass

    def getDisplayModes(self, vobj):
        return ["Flat Lines", "Shaded", "Wireframe"]

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
        pass

