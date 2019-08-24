from odd.check import Check
from odd.issue import Issue, Location


class IrModelAccessNoGroup(Check):
    _handles = {"csv_row"}

    def on_csv_row(self, csv_row):
        if csv_row.path.name.lower() != "ir.model.access.csv" or csv_row.row.get(
            "group_id:id"
        ):
            return

        permissions = [
            perm
            for perm in ("create", "read", "write", "unlink")
            if csv_row.row.get(f"perm_{perm}") == "1"
        ]
        yield Issue(
            "ir_model_access_without_group",
            f"`ir.model.access` record ({csv_row.row['id']}) allows the "
            f"following operations to users without group: "
            f"{', '.join(permissions)}",
            csv_row.addon.manifest_path,
            [Location(csv_row.path, [csv_row.line_no])],
            categories=["security", "correctness"],
        )
