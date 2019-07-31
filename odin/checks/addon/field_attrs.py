import typing

import parso
from odin.checks import PythonCheck
from odin.const import SUPPORTED_VERSIONS
from odin.issue import Issue, Location
from odin.utils import expand_version_list, get_string_node_value

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


def filter_child_nodes(node, *types: str):
    types = set(types)
    for child_node in node.children:
        if child_node.type in types:
            yield child_node


def first_child_type_node(node, type: str):
    return next(filter_child_nodes(node, type), None)


def get_model_name(classdef_node) -> typing.Optional[str]:
    model_params = {}
    suite = classdef_node.get_suite()
    for statement in filter_child_nodes(suite, "simple_stmt"):
        expr_stmt = first_child_type_node(statement, "expr_stmt")
        if expr_stmt is not None:
            if expr_stmt.children[0].type == "name":
                param = expr_stmt.children[0].value
                if param in ("_name", "_inherit"):
                    value_node = expr_stmt.children[2]
                    if value_node.type == "string":
                        model_params[param] = get_string_node_value(value_node)
    return model_params.get("_name") or model_params.get("_inherit")


def consume_name(
    node: parso.tree.Node
) -> typing.Tuple[typing.List[str], typing.List[parso.tree.NodeOrLeaf]]:
    name_parts, leftover_nodes = [], []
    for child in node.children:
        if child.type == "name":
            name_parts.append(child.value)
        elif (
            child.type == "trailer"
            and len(child.children) == 2
            and child.children[0].type == "operator"
            and child.children[0].value == "."
            and child.children[1].type == "name"
        ):
            name_parts.append(child.children[1].value)
        else:
            leftover_nodes.append(child)
    return name_parts, leftover_nodes


class FieldAttrs(PythonCheck):
    def _check_field_node(
        self, filename, addon, node, model_name: str, field_name: str, field_type: str
    ):
        assert node is None or node.type == "arglist"

        kwargs = {}
        if node is not None:
            for arg_node in node.children:
                if arg_node.type == "argument" and arg_node.children[0].type == "name":
                    kwargs[arg_node.children[0].value] = arg_node.start_pos

        if field_type not in FIELD_TYPE_VERSION_MAP.get(addon.version, set()):
            yield Issue(
                "unknown_field_type",
                f'Unknown field type "{field_type}"',
                addon.addon_path,
                [Location(filename, [node.start_pos])],
                categories=["correctness"],
            )
            return

        model_attrs = MODEL_ATTR_VERSION_MAP.get(model_name, {}).get(
            addon.version, set()
        )
        deprecated_attrs = DEPRECATED_ATTR_VERSION_MAP.get(field_type, {}).get(
            addon.version, set()
        )
        expected_attrs = (
            ATTRS_VERSION_MAP.get(field_type, {}).get(addon.version, set())
            | COMMON_ATTRS_VERSION_MAP.get(addon.version, set())
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
                    f'Deprecated field attribute "{attr}" for field type "{field_type}"',
                    addon.addon_path,
                    [Location(filename, [node.start_pos])],
                    categories=["deprecated"],
                )
                continue
            yield Issue(
                "unknown_field_attribute",
                f'Unknown field attribute "{attr}" for field type "{field_type}"',
                addon.addon_path,
                [Location(filename, [node.start_pos])],
                categories=["correctness"],
            )

    def check(self, filename, module, addon):
        for classdef in module.iter_classdefs():
            model_name = get_model_name(classdef)
            if model_name is None:
                continue

            suite = classdef.get_suite()
            for node in filter_child_nodes(suite, "simple_stmt"):
                expr_stmt_node = first_child_type_node(node, "expr_stmt")
                if expr_stmt_node is None:
                    continue

                if (
                    expr_stmt_node.children[0].type == "name"
                    and expr_stmt_node.children[1].type == "operator"
                    and expr_stmt_node.children[2].type == "atom_expr"
                ):
                    field_name = expr_stmt_node.children[0].value

                    # atom_expr
                    field_node = expr_stmt_node.children[2]
                    name_parts, leftover_nodes = consume_name(field_node)
                    if (
                        not name_parts
                        or len(name_parts) > 3
                        or len(leftover_nodes) != 1
                    ):
                        continue

                    field_type = name_parts[-1]
                    arglist = first_child_type_node(leftover_nodes[0], "arglist")

                    if len(name_parts) == 3 and (
                        name_parts[0] not in ("odoo", "openerp")
                        or name_parts[1] != "fields"
                    ):
                        continue
                    elif len(name_parts) == 2 and name_parts[0] != "fields":
                        continue
                    elif len(
                        name_parts
                    ) == 1 and field_type not in FIELD_TYPE_VERSION_MAP.get(
                        addon.version, set()
                    ):
                        continue

                    yield from self._check_field_node(
                        filename, addon, arglist, model_name, field_name, field_type
                    )
