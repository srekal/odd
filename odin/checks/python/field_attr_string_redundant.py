import logging
import typing

from odin.checks import PythonCheck
from odin.const import SUPPORTED_VERSIONS
from odin.issue import Issue, Location
from odin.parso_utils import column_index_1, get_model_definition
from odin.utils import expand_version_list

_LOG = logging.getLogger(__name__)
FIELD_TYPE_VERSION_MAP = expand_version_list(
    {
        ">=8": {
            "Binary",
            "Boolean",
            "Char",
            "Date",
            "Datetime",
            "Float",
            "Html",
            "Id",
            "Integer",
            "Many2many",
            "Many2one",
            "One2many",
            "Reference",
            "Selection",
            "Serialized",
            "Text",
        },
        ">=9": {"Monetary"},
    },
    *SUPPORTED_VERSIONS,
    result_cls=set,
)
FIELD_TYPE_STRING_INDEX_MAP = {"One2many": 2, "Many2one": 1, "Many2many": 4}


def get_odoo_string_compute_func(version: int) -> typing.Callable[[str], str]:
    def _func_lt_11(field_name: str) -> str:
        return field_name.replace("_", " ").capitalize()

    def _func_gt_11(field_name: str) -> str:
        return (
            (
                field_name[:-4]
                if field_name.endswith("_ids")
                else field_name[:-3]
                if field_name.endswith("_id")
                else field_name
            )
            .replace("_", " ")
            .title()
        )

    return _func_gt_11 if version >= 11 else _func_lt_11


class FieldAttrStringRedundant(PythonCheck):
    def check(self, addon, filename, module):
        known_fields = FIELD_TYPE_VERSION_MAP.get(addon.version, set())
        get_odoo_string = get_odoo_string_compute_func(addon.version)
        for classdef in module.iter_classdefs():
            model = get_model_definition(classdef, extract_fields=True)
            if model is None:
                continue

            for field in model.fields:
                if field.class_name not in known_fields:
                    _LOG.warning("Unknown field type: %s", field.class_name)
                    continue

                string_kwarg = None
                for kwarg in field.kwargs:
                    if kwarg.name == "string":
                        string_kwarg = kwarg
                        break
                if string_kwarg and string_kwarg.value == get_odoo_string(field.name):
                    yield Issue(
                        "redundant_field_attribute",
                        f'Redundant field attribute `string="{string_kwarg.value}"` '
                        f'for field "{field.name}". The same value will be computed '
                        f"by Odoo automatically.",
                        addon.addon_path,
                        [Location(filename, [column_index_1(string_kwarg.start_pos)])],
                        categories=["redundancy"],
                    )
                    continue

                if field.args:
                    arg_index = FIELD_TYPE_STRING_INDEX_MAP.get(field.class_name, 0)
                    if len(field.args) < arg_index + 1:
                        continue
                    string_arg = field.args[arg_index]

                    if string_arg.value == get_odoo_string(field.name):
                        yield Issue(
                            "redundant_field_attribute",
                            f"Redundant implied field attribute `string` "
                            f'"{string_arg.value}"` for field "{field.name}". '
                            f"The same value will be computed by Odoo automatically.",
                            addon.addon_path,
                            [
                                Location(
                                    filename, [column_index_1(string_arg.start_pos)]
                                )
                            ],
                            categories=["redundancy"],
                        )
                        continue
