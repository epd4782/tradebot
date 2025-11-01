from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Tuple

TEST_ROOT = Path(file).resolve().parents[1] / "tests"
SRC_ROOT = Path(file).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
sys.path.insert(0, str(SRC_ROOT))

class SkipTest(Exception):
"""Raised to indicate a skipped test or module."""

class MonkeyPatch:
def __init__(self) -> None:
self._env_changes: list[Tuple[str, str | None]] = []
self._attr_changes: list[Tuple[Any, str, Any, bool]] = []

def setenv(self, name: str, value: Any) -> None:
    old = os.environ.get(name)
    os.environ[name] = str(value)
    self._env_changes.append((name, old))

def delenv(self, name: str, raising: bool = True) -> None:
    if name in os.environ:
        old = os.environ.pop(name)
        self._env_changes.append((name, old))
    elif raising:
        raise KeyError(name)
    else:
        self._env_changes.append((name, None))

def setattr(self, target: Any, name: str, value: Any) -> None:
    existed = hasattr(target, name)
    old = getattr(target, name, None)
    setattr(target, name, value)
    self._attr_changes.append((target, name, old, existed))

def undo(self) -> None:
    while self._env_changes:
        name, old = self._env_changes.pop()
        if old is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old
    while self._attr_changes:
        target, name, old, existed = self._attr_changes.pop()
        if existed:
            setattr(target, name, old)
        else:
            delattr(target, name)
def importorskip(module_name: str) -> ModuleType:
try:
return importlib.import_module(module_name)
except Exception as exc: # pragma: no cover - dependency missing
raise SkipTest(f"missing optional dependency: {module_name}") from exc

pytest_stub = ModuleType("pytest")
pytest_stub.importorskip = importorskip # type: ignore[attr-defined]
pytest_stub.SkipTest = SkipTest # type: ignore[attr-defined]
sys.modules.setdefault("pytest", pytest_stub)

def _load_module(path: Path) -> ModuleType:
spec = importlib.util.spec_from_file_location(path.stem, path)
if spec is None or spec.loader is None:
raise ImportError(f"Cannot load module from {path}")
module = importlib.util.module_from_spec(spec)
try:
spec.loader.exec_module(module)
except SkipTest:
raise
return module

def _build_fixtures(func: Callable[..., Any]) -> Tuple[Dict[str, Any], list[Tuple[str, Any]]]:
fixtures: Dict[str, Any] = {}
cleanup: list[Tuple[str, Any]] = []
signature = inspect.signature(func)
for name in signature.parameters:
if name == "tmp_path":
tmp_dir = Path(tempfile.mkdtemp())
fixtures[name] = tmp_dir
cleanup.append((name, tmp_dir))
elif name == "monkeypatch":
fixtures[name] = MonkeyPatch()
cleanup.append((name, fixtures[name]))
else:
raise TypeError(f"Unsupported fixture '{name}' in {func.name}")
return fixtures, cleanup

def _cleanup_fixtures(cleanup: list[Tuple[str, Any]]) -> None:
for name, value in reversed(cleanup):
if name == "tmp_path":
shutil.rmtree(value, ignore_errors=True)
elif name == "monkeypatch":
value.undo()

def run() -> int:
passed = skipped = failed = 0
for test_file in sorted(TEST_ROOT.glob("test_*.py")):
try:
module = _load_module(test_file)
except SkipTest as exc:
skipped += 1
print(f"SKIPPED {test_file.name}: {exc}")
continue
except Exception as exc: # pragma: no cover - import errors
failed += 1
print(f"ERROR importing {test_file.name}: {exc}")
traceback.print_exc()
continue

    members = inspect.getmembers(module, inspect.isfunction)
    test_functions = [func for name, func in members if name.startswith("test_")]
    for func in test_functions:
        fixtures, cleanup = _build_fixtures(func)
        try:
            func(**fixtures)
        except SkipTest as exc:
            skipped += 1
            print(f"SKIPPED {func.__name__}: {exc}")
        except AssertionError as exc:
            failed += 1
            print(f"FAILED {func.__name__}: {exc}")
        except Exception as exc:  # pragma: no cover - unexpected failure
            failed += 1
            print(f"ERROR {func.__name__}: {exc}")
            traceback.print_exc()
        else:
            passed += 1
        finally:
            _cleanup_fixtures(cleanup)

print(f"Summary: {passed} passed, {failed} failed, {skipped} skipped")
return 0 if failed == 0 else 1
if name == "main":
sys.exit(run())
