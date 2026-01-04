import os
import FreeCAD as App
import FreeCADGui as Gui
# Part is handled in draw_helpers when needed

from pivy import coin

from .wall_assembly import WallAssembly
from .draw_helpers import DrawState

translate = App.Qt.translate
QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

ICONPATH = os.path.join(os.path.dirname(__file__), "resources/icons")

class DrawWallCommand:
    def GetResources(self):
        return {
            'MenuText': translate("Commands", "New Wall"),
            'ToolTip': translate("Commands", "Create a new wall object"),
            'Pixmap': os.path.join(ICONPATH, "new_wall.svg")
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        
        try:
            self.view = Gui.ActiveDocument.ActiveView
            self.doc = App.ActiveDocument
        except Exception:
            return

        self.start_point = None
        self.current_point = None
        self.wall_thickness = 90
        self.angle_lock = True
        # Z level to draw on (default 0). Change this attribute before activating
        # to draw on another level programmatically: `DrawWallCommand.level_z = 1000`.
        self.level_z = 0

        # helper state (handles preview and snapping)
        self.state = None

        

        try:
            self.callback = self.view.addEventCallback("SoEvent", self.onEvent)
            
        except Exception:
            
            self.callback = None
        # initialize DrawState after view/doc are set
        try:
            self.state = DrawState(self.view, self.doc, self.level_z, self.wall_thickness)
        except Exception:
            self.state = None
        self.active = True


    def finish(self):
        # mark inactive first so onEvent stops processing immediately
        self.active = False

        try:
            if self.view:
                # Try removing by callback id (some builds return an id)
                try:
                    if self.callback is not None:
                        self.view.removeEventCallback("SoEvent", self.callback)
                except Exception:
                    pass
                # Also try removing by function reference
                try:
                    self.view.removeEventCallback("SoEvent", self.onEvent)
                except Exception:
                    pass
        except Exception:
            pass
        self.callback = None
        self.start_point = None
        self.current_point = None
        # cleanup preview/marker if present
        if self.state is not None:
            try:
                self.state.cleanup_preview()
            except Exception:
                pass
            try:
                self.state.cleanup_marker()
            except Exception:
                pass

    # ----------------------------
    # Event handler
    # ----------------------------
    def onEvent(self, event):
        # Ignore events when not active
        if not getattr(self, "active", True):
            return

        

        # Some FreeCAD builds wrap SoEvent objects into plain dicts.
        # Support both: unwrap dicts into a tiny wrapper providing
        # the minimal methods our handlers expect (`getPosition`,
        # `getButton`, `getState`, `getKey`).
        if isinstance(event, dict):
            

            class _EvWrap:
                def __init__(self, d):
                    self._d = d

                def getPosition(self):
                    return self._d.get("Position") or self._d.get("pos") or self._d.get("position")

                def getButton(self):
                    return self._d.get("Button") or self._d.get("button") or self._d.get("button1")

                def getState(self):
                    return self._d.get("State") or self._d.get("state") or self._d.get("Action")

                def getKey(self):
                    return self._d.get("Key") or self._d.get("key")

            ev = _EvWrap(event)

            evtype = (event.get("Type") or event.get("type") or "").lower()

            # Classify event by Type string when explicit Button/Key fields are missing
            if "button" in evtype or "mouse" in evtype:
                # treat as mouse button event; consider 'down' states as clicks
                state = event.get("State") or event.get("state") or ""
                if isinstance(state, str) and "down" in state.lower():
                    self.onClick(ev)
                elif isinstance(state, int) and state == 1:
                    self.onClick(ev)
                else:
                    # if no explicit state but Type implies a press, call onClick
                    if "press" in evtype or "down" in evtype:
                        self.onClick(ev)
            elif "location" in evtype or "position" in event:
                self.onMove(ev)
            elif "keyboard" in evtype or "key" in event:
                self.onKey(ev)
            return

        # Fallback: handle native coin events
        if isinstance(event, coin.SoMouseButtonEvent):
            if event.getButton() == coin.SoMouseButtonEvent.BUTTON1 and \
               event.getState() == coin.SoMouseButtonEvent.DOWN:
                self.onClick(event)

        elif isinstance(event, coin.SoLocation2Event):
            self.onMove(event)

        elif isinstance(event, coin.SoKeyboardEvent):
            self.onKey(event)

    def onClick(self, event):
        # If event indicates a right-click, cancel the tool
        try:
            btn = event.getButton()
        except Exception:
            btn = None

        # Also check raw dict payload when present (our wrapper stores it in _d)
        raw_btn = None
        if hasattr(event, "_d"):
            raw_btn = event._d.get("Button") or event._d.get("button")

        cancelled = False
        try:
            if btn is not None:
                if isinstance(btn, str):
                    sb = btn.lower()
                    if "right" in sb or "button3" in sb or sb.endswith("3"):
                        cancelled = True
                elif isinstance(btn, int):
                    if btn in (3, coin.SoMouseButtonEvent.BUTTON3):
                        cancelled = True
        except Exception:
            pass

        if not cancelled and raw_btn is not None:
            try:
                if isinstance(raw_btn, str) and ("right" in raw_btn.lower() or "button3" in raw_btn.lower()):
                    cancelled = True
                elif isinstance(raw_btn, int) and raw_btn in (3, coin.SoMouseButtonEvent.BUTTON3):
                    cancelled = True
            except Exception:
                pass

        if cancelled:
            
            if self.state is not None:
                try:
                    self.state.cleanup_preview()
                except Exception:
                    pass
            if self.state is not None:
                try:
                    self.state.cleanup_marker()
                except Exception:
                    pass
            self.finish()
            return

        pos = event.getPosition()
        point = self.view.getPoint(pos[0], pos[1])
        try:
            point.z = self.level_z
        except Exception:
            try:
                point = App.Vector(point[0], point[1], self.level_z)
            except Exception:
                pass

        # snap to nearby geometry via helper state
        if self.state is not None:
            point = self.state.snap_point(point, start_point=self.start_point)
        else:
            try:
                tmp = DrawState(self.view, self.doc, self.level_z, self.wall_thickness)
                point = tmp.snap_point(point, start_point=self.start_point)
            except Exception:
                pass
            try:
                point.z = self.level_z
            except Exception:
                # If getPoint returns a sequence instead of Vector, construct one
                try:
                    point = App.Vector(point[0], point[1], self.level_z)
                except Exception:
                    pass

        shift_down = False
        if hasattr(event, "_d"):
            shift_down = bool(event._d.get("ShiftDown"))

        if self.start_point is None:
            # Use the snapped point as the start. Also set the current
            # point to the same snapped location so the preview reflects
            # the snapped start immediately (avoids starting at raw pointer).
            self.start_point = point
            self.current_point = point
            
            try:
                if self.state is not None:
                    self.state.update_preview(self.start_point, self.current_point)
                    try:
                        self.state.cleanup_marker()
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            # Ensure we have a current_point (if user clicked without moving)
            if self.current_point is None:
                self.current_point = point
            self.createWallAssembly(self.start_point, self.current_point)
            if self.state is not None:
                try:
                    self.state.cleanup_preview()
                except Exception:
                    pass
            if shift_down:
                # continue drawing; start next wall at this end point
                self.start_point = self.current_point
                self.current_point = None
                
            else:
                self.finish()

    def onMove(self, event):
        pos = event.getPosition()
        point = self.view.getPoint(pos[0], pos[1])
        try:
            point.z = self.level_z
        except Exception:
            try:
                point = App.Vector(point[0], point[1], self.level_z)
            except Exception:
                pass

        # snap during move for visual guidance
        if self.state is not None:
            point = self.state.snap_point(point, start_point=self.start_point)
        else:
            try:
                tmp = DrawState(self.view, self.doc, self.level_z, self.wall_thickness)
                point = tmp.snap_point(point, start_point=self.start_point)
            except Exception:
                pass
        try:
            point.z = self.level_z
        except Exception:
            try:
                point = App.Vector(point[0], point[1], self.level_z)
            except Exception:
                pass

        # If start not yet set, show the cursor marker and return
        if self.start_point is None:
            if self.state is not None:
                try:
                    self.state.update_cursor_marker(point)
                except Exception:
                    pass
            return

        # angle lock only applies once we have a start point
        if self.angle_lock:
            if self.state is not None:
                point = self.state.lock_orthogonal(self.start_point, point)
            else:
                dx = point.x - self.start_point.x
                dy = point.y - self.start_point.y
                if abs(dx) > abs(dy):
                    point = App.Vector(point.x, self.start_point.y, self.level_z)
                else:
                    point = App.Vector(self.start_point.x, point.y, self.level_z)

        self.current_point = point
        if self.state is not None:
            self.state.update_preview(self.start_point, point)

    

    def onKey(self, event):
        try:
            key = event.getKey()
        except Exception:
            key = None

        # Toggle angle lock with left control if available
        try:
            if key == coin.SoKeyboardEvent.LEFT_CONTROL:
                self.angle_lock = event.getState() != coin.SoKeyboardEvent.DOWN
                return
        except Exception:
            pass

        # Also support string key names and dict-wrapped events
        raw_key = None
        if hasattr(event, "_d"):
            raw_key = event._d.get("Key") or event._d.get("key")

        cancelled = False
        try:
            if isinstance(key, str) and key.lower() in ("esc", "escape"):
                cancelled = True
            elif isinstance(key, int) and key == 27:
                cancelled = True
        except Exception:
            pass

        if not cancelled and raw_key is not None:
            try:
                if isinstance(raw_key, str) and raw_key.lower() in ("esc", "escape"):
                    cancelled = True
                elif isinstance(raw_key, int) and raw_key == 27:
                    cancelled = True
            except Exception:
                pass

        if cancelled:
            
            if self.state is not None:
                try:
                    self.state.cleanup_preview()
                except Exception:
                    pass
            self.finish()
            return

        # Keyboard toggles
        try:
            # If user presses 'G' toggle Draft snap via workbench command
            if isinstance(key, str) and key.upper() == 'G':
                try:
                    Gui.runCommand('BuildQ_ToggleDraftSnap')
                except Exception:
                    pass
                return
        except Exception:
            pass

    # helper methods moved to draw_helpers.DrawState

    # ----------------------------
    # Final creation
    # ----------------------------
    def createWallAssembly(self, p1, p2):
        
        wall = self.doc.addObject(
            "Part::FeaturePython", "WallAssembly"
        )
        WallAssembly(wall)
        # Attach a minimal view provider so DisplayMode is available
        try:
            from .wall_assembly import WallViewProvider
            try:
                WallViewProvider(wall.ViewObject)
            except Exception:
                # older API: set proxy on ViewObject
                try:
                    wall.ViewObject.Proxy = WallViewProvider(wall.ViewObject)
                except Exception:
                    pass
        except Exception:
            pass

        wall.Start = p1
        wall.End = p2
        wall.Thickness = self.wall_thickness

        wall.ViewObject.LineWidth = 2.0
        self.doc.recompute()
        try:
            wall.ViewObject.Visibility = True
            # prefer shaded or flat lines so faces are visible
            try:
                wall.ViewObject.DisplayMode = "Flat Lines"
            except Exception:
                try:
                    wall.ViewObject.DisplayMode = "Shaded"
                except Exception:
                    pass
            try:
                wall.ViewObject.Transparency = 0
            except Exception:
                pass
            try:
                wall.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
            except Exception:
                pass
            try:
                Gui.ActiveDocument.ActiveView.fitAll()
            except Exception:
                pass
            # (removed Part.show fallback)
        except Exception:
            pass

Gui.addCommand("BuildQ_DrawWall", DrawWallCommand())