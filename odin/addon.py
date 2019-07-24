import ast
import dataclasses
import pathlib
import typing

from odin.const import MANIFEST_FILENAMES
from odin.typedefs import OdooVersion


@dataclasses.dataclass(unsafe_hash=True)
class AddonPath:
    manifest_path: pathlib.Path

    @property
    def path(self) -> pathlib.Path:
        return self.manifest_path.parent

    @property
    def name(self) -> str:
        return self.path.name


@dataclasses.dataclass
class Addon(AddonPath):
    manifest: typing.Dict[str, typing.Any]
    version: OdooVersion

    @property
    def addon_path(self) -> AddonPath:
        return AddonPath(self.manifest_path)

    @property
    def data_files(self):
        return [self.path / fn for fn in (self.manifest.get("data") or [])]

    @property
    def demo_files(self):
        return [self.path / fn for fn in (self.manifest.get("demo") or [])]

    @property
    def qweb_files(self):
        files = []
        for fn in self.manifest.get("qweb") or []:
            fn_path = self.path / fn
            if "*" in fn_path.stem:
                files.extend(fn_path.parent.glob(fn_path.name))
            else:
                files.append(fn_path)
        return files


def parse_manifest(addon_path: AddonPath):
    # FIXME: Check for manifest file size.
    with addon_path.manifest_path.open(mode="r") as f:
        return ast.literal_eval(f.read())


def find_manifest(path: pathlib.Path) -> typing.Optional[pathlib.Path]:
    for child in path.iterdir():
        if child.is_file() and child.name in MANIFEST_FILENAMES:
            return child


def discover_addons(
    dir_path: pathlib.Path
) -> typing.Generator[pathlib.Path, None, None]:
    for child in dir_path.iterdir():
        if child.is_dir():
            manifest = find_manifest(child)
            if manifest:
                yield manifest
            else:
                yield from discover_addons(child)
