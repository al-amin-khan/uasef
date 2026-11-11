# Standalone installation and packaging

Normal pip installs use resources bundled inside `uasef/_resources`: workflows,
templates, policies, roles, skills, schemas, framework metadata and Lefthook config.
Editable installs keep reading the canonical source checkout directories. Neither
mode depends on the current working directory. Generated projects keep their own
copies; reinstalling UASEF does not overwrite them. Use `uasef upgrade` explicitly.

Build from a checkout with Python 3.10 or newer:

```powershell
python -m pip install build
python -m build
```

The default build produces a source archive and a wheel built from that archive.
Install the wheel into a separate environment (adjust its filename for future versions):

```powershell
py -m venv C:\tools\uasef-env
C:\tools\uasef-env\Scripts\python.exe -m pip install dist/uasef-0.4.0-py3-none-any.whl
C:\tools\uasef-env\Scripts\uasef.exe doctor --project C:\path\to\project
```

On Linux, use `python3 -m venv ~/uasef-env` and the executables in `~/uasef-env/bin`.
The source checkout can be removed after a normal wheel installation; editable
installations still need it. Installing a wheel does not install Git, agents,
Lefthook or Cocogitto, activate hooks, authenticate providers, or publish to PyPI.
No PyPI availability is implied by these commands.

Maintainers: `setup.py` copies the canonical resource files during wheel builds;
`MANIFEST.in` includes them in source archives. No generated resource copies are
committed. Add new resource types to both rules and the package test when needed.
Build from a clean checkout to avoid stale build outputs.

`python scripts/test_package.py` builds the distribution, compares bundled resource
bytes against the source, installs into a fresh virtual environment, and runs init,
upgrade, doctor and memory commands from outside the checkout. It verifies resources
resolve inside that environment and customized project instructions survive upgrade.
CI runs this on Windows/Linux and Python 3.10/3.12. Building requires access to build
dependencies; installing the resulting wheel itself has no runtime dependencies.
