import dataclasses
import pathlib
import typing

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
