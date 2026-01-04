import FreeCAD as App
import FreeCADGui as Gui

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

class DrawLineCommand:
    """Draw a simple line object"""

    def GetResources(self):
        return {
            "Pixmap": App.getUserAppDataDir() + "/resources/icons/draw_wall.svg",
            "MenuText": "Draw Line",
            "ToolTip": "Create a basic wall assembly"
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        App.Console.PrintMessage(translate(
            "Log",
            "Line tool has been activated") + "\n")

# Register command
Gui.addCommand("DrawLine", DrawLineCommand())

class CreateWallCommand:
    """Create a simple wall object"""

    def GetResources(self):
        return {
            "Pixmap": App.getUserAppDataDir() + "/resources/icons/draw_wall.svg",
            "MenuText": "Create Wall",
            "ToolTip": "Create a wall assembly"
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        doc = App.ActiveDocument
        box = doc.addObject("Part::Box", "Wall")
        box.Length = 4000
        box.Width = 90
        box.Height = 2700
        doc.recompute()

# Register command
Gui.addCommand("CreateWall", CreateWallCommand())

class CreateSubFloorCommand:
    """Create a simple wall object"""

    def GetResources(self):
        return {
            "Pixmap": App.getUserAppDataDir() + "/resources/icons/draw_subfloor.svg",
            "MenuText": "Create SubFloor",
            "ToolTip": "Create a subfloor assembly"
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        doc = App.ActiveDocument
        box = doc.addObject("Part::Box", "Wall")
        box.Length = 4000
        box.Width = 90
        box.Height = 2700
        doc.recompute()

# Register command
Gui.addCommand("CreateSubFloor", CreateSubFloorCommand())