from odin.checks import PythonCheck
from odin.const import SUPPORTED_VERSIONS
from odin.issue import Issue, Location
from odin.parso_utils import get_model_definition
from odin.utils import expand_version_list

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


COMMON_ATTRS_VERSION_MAP = expand_version_list(
    {
        ">=8": {
            "string",
            "help",
            "readonly",
            "required",
            "index",
            "default",
            "states",
            "groups",
            "copy",
            "oldname",
            "company_dependent",
            "change_default",
            "deprecated",
            "store",
            "inherited",
        },
        ">=8,<13": {
            # mail
            "track_visibility"
        },
        "==12": {
            # mail
            "track_sequence"
        },
        ">=10": {
            "group_operator",
            "prefetch",
            # base_sparse_field
            "sparse",
        },
        ">=13": {
            # mail
            "tracking",
            "tracking_sequence",
        },
    },
    *SUPPORTED_VERSIONS,
    result_cls=set,
)

MODEL_ATTRS_VERSION_MAPS = {
    "payment.acquirer": {">=8": {"required_if_provider"}},
    "res.config.settings": {
        ">=8": {"implied_group", "group", "default_model"},
        ">=12": {"config_parameter"},
    },
}
MODEL_ATTR_VERSION_MAP = {
    model: expand_version_list(version_map, *SUPPORTED_VERSIONS, result_cls=set)
    for model, version_map in MODEL_ATTRS_VERSION_MAPS.items()
}

DEPRECATED_ATTRS_VERSION_MAPS = {
    "Char": {">=8": {"size"}, ">=13": {"track_visibility", "track_sequence"}}
}
DEPRECATED_ATTR_VERSION_MAP = {
    model: expand_version_list(version_map, *SUPPORTED_VERSIONS, result_cls=set)
    for model, version_map in DEPRECATED_ATTRS_VERSION_MAPS.items()
}
RELATED_ATTRS = {"related", "related_sudo", "store", "depends"}
COMPUTE_ATTRS = {"compute", "inverse", "search", "store", "compute_sudo"}
FIELD_ATTRS_VERSION_MAPS = {
    "Char": {
        ">=8": {
            "translate",
            "trim",
            # pad
            "pad_content_field",
        }
    },
    "Text": {">=8": {"translate"}},
    "Html": {
        ">=8": {"translate", "sanitize", "strip_style"},
        ">=10": {
            "sanitize_tags",
            "sanitize_attributes",
            "sanitize_style",
            "strip_classes",
        },
    },
    "Selection": {
        ">=8": {"selection", "selection_add"},
        ">=10": {"group_expand"},
        ">=12": {"validate"},
    },
    "Reference": {">=8": {"selection"}},
    "Binary": {">=8": {"attachment"}},
    "Integer": {"<10": {"group_operator"}},
    "Float": {">=8": {"digits"}, "<10": {"group_operator"}},
    "Monetary": {">=9": {"currency_field"}, "==9": {"group_operator"}},
    "Many2one": {
        ">=8": {
            "auto_join",
            "ondelete",
            "comodel_name",
            "domain",
            "context",
            "delegate",
        },
        ">=10": {"group_expand"},
    },
    "One2many": {
        ">=8": {
            "comodel_name",
            "inverse_name",
            "domain",
            "context",
            "auto_join",
            "limit",
        }
    },
    "Many2many": {
        ">=8": {
            "comodel_name",
            "relation",
            "column1",
            "column2",
            "domain",
            "context",
            "limit",
        }
    },
}
ATTRS_VERSION_MAP = {
    field_type: expand_version_list(version_map, *SUPPORTED_VERSIONS, result_cls=set)
    for field_type, version_map in FIELD_ATTRS_VERSION_MAPS.items()
}


class FieldAttrs(PythonCheck):
    def check(self, addon, filename, module):
        known_fields = FIELD_TYPE_VERSION_MAP.get(addon.version, set())
        common_field_attrs = COMMON_ATTRS_VERSION_MAP.get(addon.version, set())
        for classdef in module.iter_classdefs():
            model = get_model_definition(classdef, extract_fields=True)
            if not model.name:
                continue

            for field in model.fields:
                if field.class_name not in known_fields:
                    yield Issue(
                        "unknown_field_type",
                        f'Unknown field type "{field.class_name}"',
                        addon.addon_path,
                        [Location(filename, [field.start_pos])],
                        categories=["correctness"],
                    )
                    continue

                kwargs = {kw.name: kw for kw in field.kwargs}
                model_attrs = MODEL_ATTR_VERSION_MAP.get(model.name, {}).get(
                    addon.version, set()
                )
                deprecated_attrs = DEPRECATED_ATTR_VERSION_MAP.get(
                    field.class_name, {}
                ).get(addon.version, set())
                expected_attrs = (
                    ATTRS_VERSION_MAP.get(field.class_name, {}).get(
                        addon.version, set()
                    )
                    | common_field_attrs
                    | model_attrs
                )
                if "compute" in kwargs:
                    expected_attrs |= COMPUTE_ATTRS
                if "related" in kwargs:
                    expected_attrs |= RELATED_ATTRS
                unknown_attrs = kwargs.keys() - expected_attrs

                for attr in unknown_attrs:
                    if attr in deprecated_attrs:
                        yield Issue(
                            "deprecated_field_attribute",
                            f'Deprecated field attribute "{attr}" for field type "{field.class_name}"',
                            addon.addon_path,
                            [Location(filename, [kwargs[attr].start_pos])],
                            categories=["deprecated"],
                        )
                        continue
                    yield Issue(
                        "unknown_field_attribute",
                        f'Unknown field attribute "{attr}" for field type "{field.class_name}"',
                        addon.addon_path,
                        [Location(filename, [kwargs[attr].start_pos])],
                        categories=["correctness"],
                    )
