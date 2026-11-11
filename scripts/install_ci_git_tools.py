"""Install pinned official release binaries into the ephemeral CI runner."""
import io
import os
from pathlib import Path
import platform
import tarfile
import urllib.request

if os.environ.get("GITHUB_ACTIONS") != "true":
    raise SystemExit("This installer is restricted to ephemeral GitHub Actions runners")
windows = platform.system() == "Windows"
folder = Path(os.environ["RUNNER_TEMP"]) / "uasef-git-tools"
folder.mkdir(exist_ok=True)
suffix = ".exe" if windows else ""
asset = "Windows_x86_64.exe" if windows else "Linux_x86_64"
url = "https://github.com/evilmartians/lefthook/releases/download/v2.2.2/lefthook_2.2.2_" + asset
with urllib.request.urlopen(url, timeout=60) as response:
    (folder / ("lefthook" + suffix)).write_bytes(response.read())
target = "x86_64-pc-windows-msvc" if windows else "x86_64-unknown-linux-musl"
url = f"https://github.com/cocogitto/cocogitto/releases/download/7.0.0/cocogitto-7.0.0-{target}.tar.gz"
with urllib.request.urlopen(url, timeout=60) as response:
    archive = response.read()
with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
    members = [m for m in bundle.getmembers() if m.isfile() and Path(m.name).name == "cog" + suffix]
    if len(members) != 1:
        raise SystemExit("Expected exactly one Cocogitto executable")
    (folder / ("cog" + suffix)).write_bytes(bundle.extractfile(members[0]).read())
for binary in folder.iterdir():
    binary.chmod(0o755)
with open(os.environ["GITHUB_PATH"], "a", encoding="utf-8") as stream:
    stream.write(str(folder) + "\n")
