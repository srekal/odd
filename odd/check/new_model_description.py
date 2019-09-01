from odd.check import Check
from odd.issue import Issue, Location
from odd.parso_utils import UNKNOWN, column_index_1, get_model_type
from odd.utils import odoo_source_url


class NewModelDescription(Check):
    _handles = {"model_definition"}

    def on_model_definition(self, model):
        if get_model_type(model.node) == UNKNOWN:
            return
        model_name = model.params.get("_name")
        if model.params.get("_inherit") or not model_name:
            return

        if not model.params.get("_description"):
            yield Issue(
                "no_model_description",
                f'Model "{model_name}" has no `_description` set',
                model.addon.manifest_path,
                [Location(model.path, [column_index_1(model.node.start_pos)])],
                categories=(
                    ["future-warning"] if model.addon.version < 12 else ["correctness"]
                ),
                sources=[
                    odoo_source_url(
                        "ff9ddfdacc9581361b555fd5f69e2da61800acad",
                        "odoo/models.py",
                        start=529,
                    )
                ],
            )
