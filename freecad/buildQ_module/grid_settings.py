import FreeCAD as App
import FreeCADGui as Gui
try:
    from PySide2 import QtWidgets, QtCore
except Exception:
    try:
        from PySide import QtGui as QtWidgets
        from PySide import QtCore
    except Exception:
        QtWidgets = None
        QtCore = None

PARAM_ROOT = "User parameter:Plugins/buildQ"
DEFAULT_SPACING = 100.0
DEFAULT_EXTENT = 2000.0

def _param_get():
    try:
        return App.ParamGet(PARAM_ROOT)
    except Exception:
        return None

def get_grid_settings():
    pg = _param_get()
    spacing = DEFAULT_SPACING
    extent = DEFAULT_EXTENT
    if pg is not None:
        try:
            spacing = float(pg.GetFloat('GridSpacing'))
        except Exception:
            try:
                spacing = float(pg.GetDouble('GridSpacing'))
            except Exception:
                pass
        try:
            extent = float(pg.GetFloat('GridExtent'))
        except Exception:
            try:
                extent = float(pg.GetDouble('GridExtent'))
            except Exception:
                pass
    return float(spacing), float(extent)

def set_grid_settings(spacing=None, extent=None):
    pg = _param_get()
    if pg is None:
        return
    try:
        if spacing is not None:
            try:
                pg.SetFloat('GridSpacing', float(spacing))
            except Exception:
                try:
                    pg.SetDouble('GridSpacing', float(spacing))
                except Exception:
                    pg.SetString('GridSpacing', str(float(spacing)))
        if extent is not None:
            try:
                pg.SetFloat('GridExtent', float(extent))
            except Exception:
                try:
                    pg.SetDouble('GridExtent', float(extent))
                except Exception:
                    pg.SetString('GridExtent', str(float(extent)))
    except Exception:
        return


class GridSettingsDialog(QtWidgets.QDialog if QtWidgets else object):
    def __init__(self, parent=None):
        if QtWidgets:
            super(GridSettingsDialog, self).__init__(parent)
            self.setWindowTitle('BuildQ Grid Settings')
            self.setModal(True)
            self.layout = QtWidgets.QVBoxLayout(self)

            self.form = QtWidgets.QFormLayout()
            self.spin_spacing = QtWidgets.QDoubleSpinBox()
            self.spin_spacing.setRange(1.0, 100000.0)
            self.spin_spacing.setSuffix(' mm')
            self.spin_spacing.setDecimals(2)
            self.spin_extent = QtWidgets.QDoubleSpinBox()
            self.spin_extent.setRange(10.0, 100000.0)
            self.spin_extent.setSuffix(' mm')
            self.spin_extent.setDecimals(1)

            spacing, extent = get_grid_settings()
            try:
                self.spin_spacing.setValue(spacing)
                self.spin_extent.setValue(extent)
            except Exception:
                pass

            self.form.addRow('Grid spacing:', self.spin_spacing)
            self.form.addRow('Grid extent (half):', self.spin_extent)
            self.layout.addLayout(self.form)

            btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            btns.accepted.connect(self.accept)
            btns.rejected.connect(self.reject)
            self.layout.addWidget(btns)

    def get_values(self):
        if not QtWidgets:
            return get_grid_settings()
        return float(self.spin_spacing.value()), float(self.spin_extent.value())


class GridSettingsCommand:
    def GetResources(self):
        return {
            'MenuText': 'BuildQ Grid Settings',
            'ToolTip': 'Configure BuildQ grid spacing and extent',
        }

    def IsActive(self):
        return True

    def Activated(self):
        if not QtWidgets:
            App.Console.PrintMessage('PySide not available; cannot show Grid Settings dialog\n')
            return
        dlg = GridSettingsDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            s, e = dlg.get_values()
            set_grid_settings(s, e)
            App.ActiveDocument.recompute()


# register command
try:
    Gui.addCommand('BuildQ_GridSettings', GridSettingsCommand())
except Exception:
    pass
