import FreeCAD as App
import Part

 
class DrawState:
    def __init__(self, view, doc, level_z=0, wall_thickness=90):
        self.view = view
        self.doc = doc
        self.level_z = level_z
        self.wall_thickness = wall_thickness
        self.preview_obj = None

    def lock_orthogonal(self, p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        if abs(dx) > abs(dy):
            return App.Vector(p2.x, p1.y, self.level_z)
        else:
            return App.Vector(p1.x, p2.y, self.level_z)

    def make_preview_shape(self, p1, p2):
        direction = p2.sub(p1)
        if direction.Length == 0:
            return None

        direction.normalize()
        normal = App.Vector(-direction.y, direction.x, 0)
        offset = normal.multiply(self.wall_thickness / 2)

        pts = [
            p1.add(offset),
            p2.add(offset),
            p2.sub(offset),
            p1.sub(offset),
            p1.add(offset),
        ]
        return Part.makePolygon(pts)

    def update_preview(self, p1, p2):
        shape = self.make_preview_shape(p1, p2)
        if not shape:
            return

        if self.preview_obj is None:
            try:
                self.preview_obj = self.doc.addObject("Part::Feature", "WallPreview")
                try:
                    self.preview_obj.ViewObject.Transparency = 70
                except Exception:
                    pass
            except Exception:
                # fallback: try to reuse any existing object named WallPreview
                existing = self.doc.getObject("WallPreview")
                if existing:
                    self.preview_obj = existing

        if self.preview_obj is not None:
            try:
                self.preview_obj.Shape = shape
                self.doc.recompute()
            except Exception:
                pass

    def cleanup_preview(self):
        if self.preview_obj:
            try:
                self.doc.removeObject(self.preview_obj.Name)
            except Exception:
                pass
            self.preview_obj = None

    def _make_cross(self, center, size=10.0):
        # create two small perpendicular lines crossing at center
        c = center
        half = size / 2.0
        pts1 = [App.Vector(c.x - half, c.y, c.z), App.Vector(c.x + half, c.y, c.z)]
        pts2 = [App.Vector(c.x, c.y - half, c.z), App.Vector(c.x, c.y + half, c.z)]
        # return a compound of two wires
        try:
            l1 = Part.makePolygon([pts1[0], pts1[1]])
            l2 = Part.makePolygon([pts2[0], pts2[1]])
            try:
                comp = Part.makeCompound([l1, l2])
                return comp
            except Exception:
                return l1
        except Exception:
            return None

    def update_cursor_marker(self, point, size=None):
        """Create or update a small crosshair marker at `point`.
        Visible while snapping before the start point is set."""
        if point is None:
            return
        try:
            c = App.Vector(point.x, point.y, self.level_z)
        except Exception:
            try:
                c = App.Vector(point[0], point[1], self.level_z)
            except Exception:
                return

        if size is None:
            size = max(5.0, self.wall_thickness * 0.1)

        shape = self._make_cross(c, size)
        if shape is None:
            return

        if getattr(self, 'marker_obj', None) is None:
            try:
                self.marker_obj = self.doc.addObject('Part::Feature', 'WallStartMarker')
                try:
                    self.marker_obj.ViewObject.LineWidth = 2.0
                    self.marker_obj.ViewObject.LineColor = (1.0, 0.2, 0.2)
                except Exception:
                    pass
            except Exception:
                existing = self.doc.getObject('WallStartMarker')
                if existing:
                    self.marker_obj = existing

        if getattr(self, 'marker_obj', None) is not None:
            try:
                self.marker_obj.Shape = shape
            except Exception:
                pass

    def cleanup_marker(self):
        if getattr(self, 'marker_obj', None):
            try:
                self.doc.removeObject(self.marker_obj.Name)
            except Exception:
                pass
            self.marker_obj = None

    def __del__(self):
        try:
            self.cleanup_preview()
        except Exception:
            pass
        try:
            self.cleanup_marker()
        except Exception:
            pass

    def snap_point(self, point, threshold=5.0, start_point=None):
        # Determine plane from view direction
        try:
            dirv = self.view.getViewDirection()
            adx = abs(dirv.x)
            ady = abs(dirv.y)
            adz = abs(dirv.z)
        except Exception:
            adx = ady = 0.0
            adz = 1.0

        if adz >= adx and adz >= ady:
            plane = 'xy'
        elif ady >= adx and ady >= adz:
            plane = 'xz'
        else:
            plane = 'yz'

        try:
            pv = App.Vector(point.x, point.y, point.z)
        except Exception:
            try:
                pv = App.Vector(point[0], point[1], point[2])
            except Exception:
                return point

        if plane == 'xy':
            ref_u, ref_v = pv.x, pv.y
        elif plane == 'xz':
            ref_u, ref_v = pv.x, pv.z
        else:
            ref_u, ref_v = pv.y, pv.z

        best = None
        best_d = threshold
        doc = getattr(self, 'doc', App.ActiveDocument)

        preview_name = None
        if self.preview_obj is not None:
            try:
                preview_name = self.preview_obj.Name
            except Exception:
                preview_name = None

        sp_plane_u = sp_plane_v = None
        if start_point is not None:
            sp = start_point
            if plane == 'xy':
                sp_plane_u, sp_plane_v = sp.x, sp.y
            elif plane == 'xz':
                sp_plane_u, sp_plane_v = sp.x, sp.z
            else:
                sp_plane_u, sp_plane_v = sp.y, sp.z

        for obj in doc.Objects:
            try:
                # Special-case our grid object: snap only to grid intersections
                try:
                    name = getattr(obj, 'Name', None)
                except Exception:
                    name = None
                if name == 'BuildQ_Grid':
                    # determine spacing from persisted settings if available
                    spacing = 100.0
                    try:
                        import importlib
                        gs = importlib.import_module('buildQ_module.grid_settings')
                        try:
                            spacing, _ = gs.get_grid_settings()
                        except Exception:
                            spacing = getattr(gs, 'DEFAULT_SPACING', spacing)
                    except Exception:
                        try:
                            pg = App.ParamGet('User parameter:Plugins/buildQ')
                            try:
                                spacing = float(pg.GetFloat('GridSpacing'))
                            except Exception:
                                try:
                                    spacing = float(pg.GetDouble('GridSpacing'))
                                except Exception:
                                    pass
                        except Exception:
                            spacing = 100.0

                    # round reference coords to nearest grid intersection
                    ug = round(ref_u / spacing) * spacing
                    vg = round(ref_v / spacing) * spacing
                    dv = ((ug - ref_u)**2 + (vg - ref_v)**2) ** 0.5
                    if dv < best_d:
                        best_d = dv
                        if plane == 'xy':
                            best = App.Vector(ug, vg, self.level_z)
                        elif plane == 'xz':
                            best = App.Vector(ug, self.level_z, vg)
                        else:
                            best = App.Vector(self.level_z, ug, vg)
                    continue
                if preview_name is not None and getattr(obj, 'Name', None) == preview_name:
                    continue
                shp = getattr(obj, 'Shape', None)
                if not shp:
                    continue
                for v in shp.Vertexes:
                    vxp = v.Point
                    if plane == 'xy':
                        u, v2 = vxp.x, vxp.y
                    elif plane == 'xz':
                        u, v2 = vxp.x, vxp.z
                    else:
                        u, v2 = vxp.y, vxp.z
                    dv = ((u - ref_u)**2 + (v2 - ref_v)**2) ** 0.5
                    try:
                        if sp_plane_u is not None and ((u - sp_plane_u)**2 + (v2 - sp_plane_v)**2) ** 0.5 < 1e-3:
                            continue
                    except Exception:
                        pass
                    if dv < best_d:
                        best_d = dv
                        if plane == 'xy':
                            best = App.Vector(u, v2, self.level_z)
                        elif plane == 'xz':
                            best = App.Vector(u, self.level_z, v2)
                        else:
                            best = App.Vector(self.level_z, u, v2)
                for e in shp.Edges:
                    try:
                        a = e.Vertexes[0].Point
                        b = e.Vertexes[-1].Point
                        if plane == 'xy':
                            ax, ay = a.x, a.y
                            bx, by = b.x, b.y
                        elif plane == 'xz':
                            ax, ay = a.x, a.z
                            bx, by = b.x, b.z
                        else:
                            ax, ay = a.y, a.z
                            bx, by = b.y, b.z
                        vx = bx - ax
                        vy = by - ay
                        seg_len2 = vx*vx + vy*vy
                        if seg_len2 == 0:
                            continue
                        t = ((ref_u - ax) * vx + (ref_v - ay) * vy) / seg_len2
                        if t < 0:
                            cx, cy = ax, ay
                        elif t > 1:
                            cx, cy = bx, by
                        else:
                            cx = ax + t * vx
                            cy = ay + t * vy
                        dv = ((cx - ref_u)**2 + (cy - ref_v)**2) ** 0.5
                        try:
                            if sp_plane_u is not None and ((cx - sp_plane_u)**2 + (cy - sp_plane_v)**2) ** 0.5 < 1e-3:
                                continue
                        except Exception:
                            pass
                        if dv < best_d:
                            best_d = dv
                            if plane == 'xy':
                                best = App.Vector(cx, cy, self.level_z)
                            elif plane == 'xz':
                                best = App.Vector(cx, self.level_z, cy)
                            else:
                                best = App.Vector(self.level_z, cx, cy)
                    except Exception:
                        continue
            except Exception:
                continue

        return best if best is not None else point