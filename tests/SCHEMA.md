---
schema: '0.1'
coverage: listed
---

# SCHEMA — tests

> The pytest suite for the core library: what each module of `recon_engine/` promises, pinned by a test.

## Conventions

- pytest only, configured in `[tool.pytest.ini_options]` of `pyproject.toml`; CI installs nothing else, so a test needs no other third-party package.
- Arrange-Act-Assert, with the three steps marked by comments.
- No `__init__.py`: pytest collects by path, so every test module name is unique.
- Money and quantities are `Decimal` in fixtures too; a float appears only in a test that proves floats are rejected.

## Structure

| entry | kind | purpose | rules |
| --- | --- | --- | --- |
| `test_*.py` | pattern | `test_<module>.py` pins one module of `recon_engine/`; `test_package.py` holds the package-wide checks (version, public API, standard-library-only imports); `test_readme.py` runs the README's Quick start example | required |

## Placement

- A test for `recon_engine/<module>.py` → `test_<module>.py`
- A check that spans the whole package → `test_package.py`
- A check that a README example still runs as shown → `test_readme.py`
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Skipping or xfailing a test to get the suite green.
- A test that needs network access or a third-party service.
