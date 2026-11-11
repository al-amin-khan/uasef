"""Bundle canonical framework resources without duplicating them in source."""
from pathlib import Path
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py

ROOT = Path(__file__).resolve().parent
DIRECTORIES = ("agents", "skills", "policies", "templates", "workflows", "schemas")
FILES = ("framework.json", "lefthook.yml")


def resource_files():
    result = [ROOT / name for name in FILES]
    for name in DIRECTORIES:
        result.extend(p for p in (ROOT / name).rglob("*")
                      if p.is_file() and p.suffix in (".md", ".json", ".yaml", ".yml"))
    for path in result:
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise RuntimeError(f"Missing or unsafe framework resource: {path}")
    return sorted(result)


class BuildWithResources(build_py):
    def run(self):
        super().run()
        for source in resource_files():
            target = Path(self.build_lib) / "uasef" / "_resources" / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def get_outputs(self, include_bytecode=1):
        return super().get_outputs(include_bytecode) + [
            str(Path(self.build_lib) / "uasef" / "_resources" / p.relative_to(ROOT))
            for p in resource_files()]


setup(cmdclass={"build_py": BuildWithResources})
