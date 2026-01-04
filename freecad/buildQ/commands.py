import FreeCAD
import FreeCADGui

class DrawLineCommand:
    """Draw a simple line object"""

    def GetResources(self):
        return {
            "Pixmap": FreeCAD.getUserAppDataDir() + "/resources/icons/draw_wall.svg",
            "MenuText": "Draw Line",
            "ToolTip": "Create a basic wall assembly"
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        App.Console.PrintMessage(translate(
            "Log",
            "Line tool has been activated") + "\n")

# Register command
FreeCADGui.addCommand("DrawLine", DrawLineCommand())

class CreateWallCommand:
    """Create a simple wall object"""

    def GetResources(self):
        return {
            "Pixmap": FreeCAD.getUserAppDataDir() + "/resources/icons/draw_wall.svg",
            "MenuText": "Create Wall",
            "ToolTip": "Create a wall assembly"
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        box = doc.addObject("Part::Box", "Wall")
        box.Length = 4000
        box.Width = 90
        box.Height = 2700
        doc.recompute()

# Register command
FreeCADGui.addCommand("CreateWall", CreateWallCommand())

class CreateSubFloorCommand:
    """Create a simple wall object"""

    def GetResources(self):
        return {
            "Pixmap": FreeCAD.getUserAppDataDir() + "/resources/icons/draw_subfloor.svg",
            "MenuText": "Create SubFloor",
            "ToolTip": "Create a subfloor assembly"
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        box = doc.addObject("Part::Box", "Wall")
        box.Length = 4000
        box.Width = 90
        box.Height = 2700
        doc.recompute()

# Register command
FreeCADGui.addCommand("CreateWall", CreateWallCommand())