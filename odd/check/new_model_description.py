from odd.check import Check
from odd.issue import Issue, Location
from odd.parso_utils import (
    UNKNOWN,
    column_index_1,
    get_model_definition,
    get_model_type,
)
from odd.utils import odoo_source_url


class NewModelDescription(Check):
    _handles = {"python_module"}

    def on_python_module(self, python_module):
        for classdef in python_module.module.iter_classdefs():
            if get_model_type(classdef) == UNKNOWN:
                continue

            model = get_model_definition(classdef, extract_fields=True)

            model_name = model.params.get("_name")
            if model.params.get("_inherit") or not model_name:
                continue

            if not model.params.get("_description"):
                yield Issue(
                    "no_model_description",
                    f'Model "{model_name}" has no `_description` set',
                    python_module.addon.manifest_path,
                    [
                        Location(
                            python_module.path, [column_index_1(classdef.start_pos)]
                        )
                    ],
                    categories=(
                        ["future-warning"]
                        if python_module.addon.version < 12
                        else ["correctness"]
                    ),
                    sources=[
                        odoo_source_url(
                            "ff9ddfdacc9581361b555fd5f69e2da61800acad",
                            "odoo/models.py",
                            start=529,
                        )
                    ],
                )
