"""Package-wide checks: recon_engine imports, carries a version, and loads only the standard library."""

import json
import subprocess
import sys

import recon_engine

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
