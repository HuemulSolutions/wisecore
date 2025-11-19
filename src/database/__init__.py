from importlib import import_module
from pkgutil import iter_modules
from pathlib import Path

def load_models():
    pkg_path = Path(__file__).resolve().parents[1] / "modules"
    for mod in iter_modules([str(pkg_path)]):
        if (pkg_path / mod.name / "models.py").exists():
            import_module(f"src.modules.{mod.name}.models")
