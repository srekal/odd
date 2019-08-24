import csv
import pathlib

from odd.check import Check
from odd.issue import Issue, Location


class IrModelAccessNoGroup(Check):
    _handles = {"data_file", "demo_file"}

    def _check_csv(self, addon, csv_path: pathlib.Path):
        with csv_path.open(mode="r") as f:
            reader = csv.DictReader(f)
            line_no = 1
            for row in reader:
                line_no += 1
                if row.get("group_id:id"):
                    continue

                permissions = [
                    perm
                    for perm in ("create", "read", "write", "unlink")
                    if row.get(f"perm_{perm}") == "1"
                ]
                yield Issue(
                    "ir_model_access_without_group",
                    f"`ir.model.access` record ({row['id']}) allows the "
                    f"following operations to users without group: "
                    f"{', '.join(permissions)}",
                    addon.manifest_path,
                    [Location(csv_path, [line_no])],
                    categories=["security", "correctness"],
                )

    def on_data_file(self, data_file):
        if data_file.path.name.lower() == "ir.model.access.csv":
            yield from self._check_csv(data_file.addon, data_file.path)

    def on_demo_file(self, demo_file):
        if demo_file.path.name.lower() == "ir.model.access.csv":
            yield from self._check_csv(demo_file.addon, demo_file.path)
