"""README.md: the Quick start example runs and prints what the README says it prints."""

import re
import subprocess
import sys
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"


def quick_start_section():
    text = README.read_text(encoding="utf-8")
    match = re.search(r"^## Quick start\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert match, "README.md has no '## Quick start' section"
    return match.group(1)


def test_quick_start_example_prints_what_the_readme_shows():
    # Arrange
    section = quick_start_section()
    code = re.search(r"^```python\n(.*?)^```", section, re.S | re.M).group(1)
    shown = re.search(r"^```text\n(.*?)^```", section, re.S | re.M).group(1)

    # Act
    run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)

    # Assert
    assert run.stdout == shown
