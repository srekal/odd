from odd.check import Check
from odd.check.python_emitter import FIELD_TYPE_VERSION_MAP
from odd.const import SUPPORTED_VERSIONS
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1
from odd.utils import expand_version_list

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
            "company_dependent",
            "change_default",
            "deprecated",
            "store",
            "inherited",
        },
        ">=8,<13": {
            "oldname",
            # mail
            "track_visibility",
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
            "depends_context",
            # mail
            "tracking",
            "tracking_sequence",
        },
        ">10,<13": {"context_dependent"},
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

COMMON_DEPRECATED_ATTRS_VERSION_MAP = expand_version_list(
    {">=13": {"oldname"}}, *SUPPORTED_VERSIONS, result_cls=set
)
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
    "Image": {">=13": {"max_width", "max_height"}},
    "Many2oneReference": {">=13": {"model_field"}},
}
ATTRS_VERSION_MAP = {
    field_type: expand_version_list(version_map, *SUPPORTED_VERSIONS, result_cls=set)
    for field_type, version_map in FIELD_ATTRS_VERSION_MAPS.items()
}

RENAMED_ATTRS_VERSION_MAP = expand_version_list(
    {">=10": {("select", "index"), ("digits_compute", "digits")}},
    *SUPPORTED_VERSIONS,
    result_cls=set,
)


class FieldAttrs(Check):
    _handles = {"field_definition"}

    def on_field_definition(self, field):
        """
        for classdef in module.iter_classdefs():
            model = get_model_definition(classdef, extract_fields=True)
            if not model.name:
                continue

            for field in model.fields:
        """
        addon, path = field.model.addon, field.model.path
        known_fields = FIELD_TYPE_VERSION_MAP.get(addon.version, set())
        common_field_attrs = COMMON_ATTRS_VERSION_MAP.get(addon.version, set())

        if field.class_name not in known_fields:
            yield Issue(
                "unknown_field_type",
                f'Unknown field type "{field.class_name}"',
                addon.manifest_path,
                [Location(path, [column_index_1(field.start_pos)])],
                categories=["correctness"],
            )
            return

        kwargs = {kw.name: kw for kw in field.kwargs}
        model_attrs = MODEL_ATTR_VERSION_MAP.get(field.model.name, {}).get(
            addon.version, set()
        )
        deprecated_attrs = DEPRECATED_ATTR_VERSION_MAP.get(field.class_name, {}).get(
            addon.version, set()
        )
        deprecated_attrs |= COMMON_DEPRECATED_ATTRS_VERSION_MAP.get(
            addon.version, set()
        )
        expected_attrs = (
            ATTRS_VERSION_MAP.get(field.class_name, {}).get(addon.version, set())
            | common_field_attrs
            | model_attrs
        )
        if "compute" in kwargs:
            expected_attrs |= COMPUTE_ATTRS
        if "related" in kwargs:
            expected_attrs |= RELATED_ATTRS
        unknown_attrs = kwargs.keys() - expected_attrs
        renamed_attrs = dict(RENAMED_ATTRS_VERSION_MAP.get(addon.version, set()))

        for attr in unknown_attrs:
            if attr in renamed_attrs:
                yield Issue(
                    "renamed_field_attribute",
                    f'Field attribute "{attr}" '
                    f'was renamed to "{renamed_attrs[attr]}"',
                    addon.manifest_path,
                    [Location(path, [column_index_1(kwargs[attr].start_pos)])],
                    categories=["deprecated"],
                )
                continue

            if attr in deprecated_attrs:
                yield Issue(
                    "deprecated_field_attribute",
                    f'Deprecated field attribute "{attr}" '
                    f'for field type "{field.class_name}"',
                    addon.manifest_path,
                    [Location(path, [column_index_1(kwargs[attr].start_pos)])],
                    categories=["deprecated"],
                )
                continue
            yield Issue(
                "unknown_field_attribute",
                f'Unknown field attribute "{attr}" '
                f'for field type "{field.class_name}"',
                addon.manifest_path,
                [Location(path, [column_index_1(kwargs[attr].start_pos)])],
                categories=["correctness"],
            )
