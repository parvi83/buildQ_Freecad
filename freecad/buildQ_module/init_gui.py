import os
import FreeCADGui as Gui
import FreeCAD as App

translate =App.Qt.translate
QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
TRANSLATIONSPATH = os.path.join(os.path.dirname(__file__), "resources", "translations")

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()

class BuildQWorkbench(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """
    MenuText = translate("Workbench", "buildQ")
    ToolTip = translate("Workbench", "Tools to make building elements and quantify materials")
    Icon = os.path.join(ICONPATH, "cool.svg")

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """

        # Ensure the modules that register GUI commands are imported.
        # Use underscore aliases to avoid linter warnings about unused names.
        try:
            from . import draw_wall as _draw_wall
            from . import grid_tool as _grid_tool
            from . import grid_settings as _grid_settings
        except Exception:
            try:
                from freecad.buildQ_module import draw_wall as _draw_wall
                from freecad.buildQ_module import grid_tool as _grid_tool
                from freecad.buildQ_module import grid_settings as _grid_settings
            except Exception:
                import importlib
                _draw_wall = importlib.import_module("buildQ_module.draw_wall")
                try:
                    _grid_tool = importlib.import_module("buildQ_module.grid_tool")
                except Exception:
                    _grid_tool = None
                try:
                    _grid_settings = importlib.import_module("buildQ_module.grid_settings")
                except Exception:
                    _grid_settings = None

        # Force-import grid modules via importlib to ensure their Gui commands register
        try:
            import importlib as _imp
            try:
                _grid_tool = _imp.import_module('buildQ_module.grid_tool')
            except Exception:
                try:
                    _grid_tool = _imp.import_module('freecad.buildQ_module.grid_tool')
                except Exception:
                    _grid_tool = _grid_tool if ' _grid_tool' in locals() else None
            try:
                _grid_settings = _imp.import_module('buildQ_module.grid_settings')
            except Exception:
                try:
                    _grid_settings = _imp.import_module('freecad.buildQ_module.grid_settings')
                except Exception:
                    _grid_settings = _grid_settings if ' _grid_settings' in locals() else None
        except Exception:
            pass

        # Provide a small set of Draft snap/grid wrapper commands here so the
        # workbench does not depend on an external helper module.
        def _run_draft_candidate(candidates):
            for c in candidates:
                try:
                    Gui.runCommand(c)
                    return c
                except Exception:
                    continue
            return None

        class ToggleDraftSnapCommand:
            def GetResources(self):
                return {
                    'MenuText': "Toggle Draft Snap",
                    'ToolTip': "Toggle Draft snapping (tries several Draft command IDs)",
                }

            def IsActive(self):
                return True

            def Activated(self):
                candidates = ['Draft_ToggleSnap', 'Draft_Snap', 'Draft_ToggleSnapping', 'Draft_ToggleDraftSnap']
                cmd = _run_draft_candidate(candidates)
                if cmd:
                    App.Console.PrintMessage(f"Draft: ran {cmd}\n")
                else:
                    App.Console.PrintMessage("Draft: no toggle snap command found\n")

        class SnapModeCommand:
            def __init__(self, mode_name, candidates):
                self.mode_name = mode_name
                self.candidates = candidates

            def GetResources(self):
                return {
                    'MenuText': f"Snap: {self.mode_name}",
                    'ToolTip': f"Toggle Draft snap mode: {self.mode_name}",
                }

            def IsActive(self):
                return True

            def Activated(self):
                cmd = _run_draft_candidate(self.candidates)
                if cmd:
                    App.Console.PrintMessage(f"Draft: ran {cmd}\n")
                else:
                    App.Console.PrintMessage(f"Draft: no command found for snap {self.mode_name}\n")

        # Register workbench-local Draft wrapper commands
        Gui.addCommand('BuildQ_ToggleDraftSnap', ToggleDraftSnapCommand())
        Gui.addCommand('BuildQ_SnapVertex', SnapModeCommand('Vertex', ['Draft_SnapVertex', 'Draft_SnapVertexMode']))
        Gui.addCommand('BuildQ_SnapEndpoint', SnapModeCommand('Endpoint', ['Draft_SnapEndpoint', 'Draft_SnapEndpointMode']))
        Gui.addCommand('BuildQ_SnapMidpoint', SnapModeCommand('Midpoint', ['Draft_SnapMidpoint', 'Draft_SnapMidpointMode']))
        Gui.addCommand('BuildQ_SnapIntersection', SnapModeCommand('Intersection', ['Draft_SnapIntersection', 'Draft_SnapIntersectionMode']))
        Gui.addCommand('BuildQ_SnapGrid', SnapModeCommand('Grid', ['Draft_SnapGrid', 'Draft_SnapGridMode']))

        # Build toolbar command list; only include grid/settings if modules loaded
        self.commands = ["BuildQ_DrawWall"]
        if _grid_tool is not None:
            self.commands.append("BuildQ_ToggleGrid")
        if _grid_settings is not None:
            self.commands.append("BuildQ_GridSettings")
        self.commands += [
            "BuildQ_ToggleDraftSnap",
            "BuildQ_SnapVertex",
            "BuildQ_SnapEndpoint",
            "BuildQ_SnapMidpoint",
            "BuildQ_SnapIntersection",
            "BuildQ_SnapGrid",
        ]

        # NOTE: Context for this commands must be "Workbench"
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.commands)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "buildQ"), self.commands)

        


    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        

        # Try to re-enable Draft workbench grid and snapping so user prefs persist
        try:
            # attempt a few possible Draft command IDs until one succeeds
            grid_cmds = [
                'Draft_ToggleGrid', 'Draft_ToggleGridVisibility', 'Draft_ToggleGridVisible',
                'Draft_Grid',
            ]
            snap_cmds = [
                'Draft_Snap', 'Draft_ToggleSnap', 'Draft_ToggleSnapping', 'Draft_ToggleDraftSnap'
            ]
            for c in grid_cmds:
                try:
                    Gui.runCommand(c)
                    break
                except Exception:
                    continue
            for c in snap_cmds:
                try:
                    Gui.runCommand(c)
                    break
                except Exception:
                    continue
        except Exception:
            pass

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        

Gui.addWorkbench(BuildQWorkbench())
