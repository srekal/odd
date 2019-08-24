import dataclasses

from odd.check.path_emitter import AddonPath
from odd.check import Check


@dataclasses.dataclass
class DataFile(AddonPath):
    ...


@dataclasses.dataclass
class DemoFile(AddonPath):
    ...


class AddonFileEmitter(Check):
    _handles = {"addon"}
    _emits = {"data_file", "demo_file"}

    def on_addon(self, addon):
        # TODO: Handle `init`, `init_xml`, `demo_xml`.
        for path in addon.data_files:
            yield DataFile(addon, path)
        for path in addon.demo_files:
            yield DemoFile(addon, path)
