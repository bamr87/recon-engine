"""Package-wide checks: recon_engine imports, carries a version, and uses only the standard library."""

import ast
import json
import subprocess
import sys
from pathlib import Path

import recon_engine

CORE = Path(__file__).resolve().parents[1] / "recon_engine"
PUBLIC_API = [
    "EventType",
    "GLPosting",
    "JournalType",
    "MissingDirectionError",
    "MissingStandardCostError",
    "OperationalEvent",
    "Residual",
    "monthly_residual",
]

# Run in a fresh interpreter, so nothing this pytest session already imported can hide a third-party import.
# Diffing sys.modules ignores what the interpreter loads at startup (site, .pth files, the editable-install finder).
_IMPORT_PROBE = """
import json, sys
before = set(sys.modules)
import recon_engine
print(json.dumps(sorted(set(sys.modules) - before)))
"""


def test_version_is_a_non_empty_string():
    # Arrange
    version = recon_engine.__version__

    # Act
    is_text = isinstance(version, str)

    # Assert
    assert is_text
    assert version.strip()


def test_import_loads_only_the_standard_library():
    # Arrange
    allowed = set(sys.stdlib_module_names) | {"recon_engine"}

    # Act
    probe = subprocess.run([sys.executable, "-c", _IMPORT_PROBE], capture_output=True, text=True, check=True)
    loaded = {name.partition(".")[0] for name in json.loads(probe.stdout)}

    # Assert
    assert "recon_engine" in loaded
    assert sorted(loaded - allowed) == []


def test_core_source_imports_only_the_standard_library():
    # Arrange: every module on disk, including any that __init__ does not import.
    sources = sorted(CORE.rglob("*.py"))
    allowed = set(sys.stdlib_module_names)

    # Act
    outside = []
    for path in sources:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            else:
                continue  # not an import, or a relative import within the package
            outside += [f"{path.name}: {name}" for name in names if name.partition(".")[0] not in allowed]

    # Assert
    assert {path.name for path in sources} >= {"__init__.py", "schemas.py", "residual.py"}
    assert outside == []


def test_public_api_is_exported():
    # Arrange
    expected = set(PUBLIC_API)

    # Act
    exported = set(recon_engine.__all__)

    # Assert
    assert exported == expected
    assert all(hasattr(recon_engine, name) for name in expected)
