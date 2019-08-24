import csv
import dataclasses
import typing

from odd.check import Check
from odd.check.path_emitter import AddonPath


@dataclasses.dataclass
class CSVRow(AddonPath):
    row: typing.Dict[str, typing.Any]
    line_no: int


class CSVRowEmitter(Check):
    _handles = {"data_file", "demo_file"}
    _emits = {"csv_row"}

    def _load_csv(self, addon_path):
        if addon_path.path.suffix.lower() != ".csv":
            return
        with addon_path.path.open(mode="r") as f:
            for idx, row in enumerate(csv.DictReader(f), start=2):
                yield CSVRow(addon_path.addon, addon_path.path, row, idx)

    on_data_file = on_demo_file = _load_csv
