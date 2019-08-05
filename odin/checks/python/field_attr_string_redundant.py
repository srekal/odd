import logging
import typing

from odin.checks import PythonCheck
from odin.const import SUPPORTED_VERSIONS
from odin.issue import Issue, Location
from odin.parso_utils import get_model_definition
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

                for kwarg in field.kwargs:
                    if kwarg.name != "string":
                        continue
                    if kwarg.value == get_odoo_string(field.name):
                        yield Issue(
                            "redundant_field_attribute",
                            f'Redundant field attribute `string="{kwarg.value}"` for field "{field.name}". The same value will be computed by Odoo automatically.',
                            addon.addon_path,
                            [Location(filename, [kwarg.start_pos])],
                            categories=["redundancy"],
                        )
