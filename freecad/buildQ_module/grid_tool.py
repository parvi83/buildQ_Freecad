import FreeCAD as App
import FreeCADGui as Gui
import Part
try:
	from pivy import coin
except Exception:
	coin = None

ICON_NAME = "BuildQ_Grid"
GRID_SPACING = 100.0

# module-level handle to the GUI overlay node so we can toggle it
_grid_overlay = None

def _create_grid(doc, spacing=100.0, extent=2000.0, z=0.0):
	# create a set of line wires forming a square grid centered at origin
	lines = []
	try:
		n = int(extent // spacing)
	except Exception:
		n = int(2000 // 100)
	rng = range(-n, n+1)
	for i in rng:
		x = i * spacing
		# vertical line
		p1 = App.Vector(x, -extent, z)
		p2 = App.Vector(x, extent, z)
		try:
			lines.append(Part.makePolygon([p1, p2]))
		except Exception:
			continue
	for j in rng:
		y = j * spacing
		p1 = App.Vector(-extent, y, z)
		p2 = App.Vector(extent, y, z)
		try:
			lines.append(Part.makePolygon([p1, p2]))
		except Exception:
			continue
	if not lines:
		return None
	try:
		compound = Part.makeCompound(lines)
		return compound
	except Exception:
		# fallback: return first line
		return lines[0]

class ToggleGridCommand:
	def GetResources(self):
		return {
			'MenuText': 'Toggle BuildQ Grid',
			'ToolTip': 'Toggle the BuildQ workbench grid',
		}

	def IsActive(self):
		return App.ActiveDocument is not None

	def Activated(self):
		doc = App.ActiveDocument
		if doc is None:
			return

		global _grid_overlay

		spacing = GRID_SPACING
		extent = 2000.0

		try:
			import importlib
			gs = importlib.import_module('buildQ_module.grid_settings')
			try:
				spacing, extent = gs.get_grid_settings()
			except Exception:
				spacing = getattr(gs, 'DEFAULT_SPACING', spacing)
				extent = getattr(gs, 'DEFAULT_EXTENT', extent)
		except Exception:
			pass

		# --- fallback: document object grid (no Coin) ---
		if coin is None:
			existing = doc.getObject(ICON_NAME)
			if existing:
				try:
					doc.removeObject(existing.Name)
				except Exception:
					pass
				return

			grid = doc.addObject('Part::Feature', ICON_NAME)
			shape = _create_grid(doc, spacing=spacing, extent=extent, z=0.0)
			if shape:
				grid.Shape = shape
				try:
					grid.ViewObject.LineWidth = 1.0
					grid.ViewObject.LineColor = (0.7, 0.7, 0.7)
					grid.ViewObject.Transparency = 80
					grid.ViewObject.Selectable = False
				except Exception:
					pass

			doc.recompute()
			return

		# --- Coin overlay grid ---
		try:
			view = Gui.ActiveDocument.ActiveView
		except Exception:
			try:
				view = Gui.ActiveDocument.getActiveView()
			except Exception:
				return

		try:
			sg = view.getSceneGraph()
		except Exception:
			try:
				sg = view.getSceneRoot()
			except Exception:
				return

		if _grid_overlay and sg:
			try:
				sg.removeChild(_grid_overlay)
			except Exception:
				pass
			_grid_overlay = None
			return

		root = coin.SoSeparator()

		pick = coin.SoPickStyle()
		pick.style = coin.SoPickStyle.UNPICKABLE
		root.addChild(pick)

		mat = coin.SoMaterial()
		mat.diffuseColor = coin.SbColor(0.7, 0.7, 0.7)
		root.addChild(mat)

		n = int(extent // spacing)
		rng = range(-n, n + 1)

		for i in rng:
			x = i * spacing
			coords = coin.SoCoordinate3()
			coords.point.set1Value(0, (x, -extent, 0))
			coords.point.set1Value(1, (x, extent, 0))
			lines = coin.SoLineSet()
			lines.numVertices.set1Value(0, 2)
			root.addChild(coords)
			root.addChild(lines)

		for j in rng:
			y = j * spacing
			coords = coin.SoCoordinate3()
			coords.point.set1Value(0, (-extent, y, 0))
			coords.point.set1Value(1, (extent, y, 0))
			lines = coin.SoLineSet()
			lines.numVertices.set1Value(0, 2)
			root.addChild(coords)
			root.addChild(lines)

		try:
			sg.addChild(root)
			_grid_overlay = root
		except Exception:
			_grid_overlay = None

# register command
Gui.addCommand('BuildQ_ToggleGrid', ToggleGridCommand())
