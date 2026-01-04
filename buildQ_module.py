# Shim to expose nested freecad/buildQ_module as top-level package `buildQ_module`
# This lets FreeCAD import `buildQ_module` when the actual package is nested
# under the `freecad` subdirectory in this module folder.
import importlib.util
import sys
import os

_pkg_dir = os.path.join(os.path.dirname(__file__), "freecad", "buildQ_module")
_init = os.path.join(_pkg_dir, "__init__.py")

if os.path.exists(_init):
    spec = importlib.util.spec_from_file_location(
        "buildQ_module", _init, submodule_search_locations=[_pkg_dir]
    )
    module = importlib.util.module_from_spec(spec)
    module.__path__ = [_pkg_dir]
    sys.modules["buildQ_module"] = module
    spec.loader.exec_module(module)
else:
    # Fallback: add the nested `freecad` folder to sys.path so imports succeed.
    freecad_dir = os.path.join(os.path.dirname(__file__), "freecad")
    if freecad_dir not in sys.path:
        sys.path.insert(0, freecad_dir)
