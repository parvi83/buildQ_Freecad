import os
import FreeCADGui as Gui
import FreeCAD as App

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
TRANSLATIONSPATH = os.path.join(os.path.dirname(__file__), "resources", "translations")

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()

class buildQWorkbench(Gui.Workbench):
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

        import freecad.buildQ.commands # noqa: F401

        self.commands = ["DrawLine", "CreateWall", "CreateSubFloor"]

        App.Console.PrintMessage(translate(
            "Log",
            "Switching to buildQ") + "\n")

        # NOTE: Context for this commands must be "Workbench"
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.commands)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.commands)

    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench buildQ_module activated.") + "\n")

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench buildQ_module de-activated.") + "\n")


Gui.addWorkbench(buildQWorkbench())