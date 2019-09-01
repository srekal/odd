import dataclasses
import typing

import parso

from odd.artifact import Artifact
from odd.check import Check
from odd.check.path_emitter import AddonPath
from odd.const import UNKNOWN, SUPPORTED_VERSIONS
from odd.utils import expand_version_list
from odd.parso_utils import (
    ATOM_EXPR_NODE_TYPES,
    STRING_NODE_TYPES,
    Position,
    consume_name,
    filter_child_nodes,
    first_child_type_node,
    get_bases,
    get_node_value,
    get_parso_grammar,
    get_string_node_value,
)


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
        ">=13": {"Image", "Many2oneReference"},
    },
    *SUPPORTED_VERSIONS,
    result_cls=set,
)


@dataclasses.dataclass
class PythonModule(AddonPath):
    module: parso.python.tree.Module


@dataclasses.dataclass
class FieldArg:
    value: typing.Any
    start_pos: Position
    end_pos: Position


@dataclasses.dataclass
class FieldKwarg:
    name: str
    value: typing.Any
    start_pos: Position
    end_pos: Position


@dataclasses.dataclass
class ModelDefinition(AddonPath):
    node: parso.tree.Node
    class_name: str
    params: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
    bases: typing.List = dataclasses.field(default_factory=list)

    @property
    def name(self) -> typing.Optional[str]:
        return _get_model_name(self.params)


@dataclasses.dataclass
class FieldDefinition(Artifact):
    name: str
    class_name: str
    model: ModelDefinition
    start_pos: Position
    end_pos: Position
    args: typing.List[FieldArg] = dataclasses.field(default_factory=list)
    kwargs: typing.List[FieldKwarg] = dataclasses.field(default_factory=list)


def _get_model_params(
    classdef_node: parso.python.tree.Class
) -> typing.Dict[str, typing.Any]:
    model_params = {}
    suite = classdef_node.get_suite()
    for child in suite.children:
        if child.type == "simple_stmt":
            expr_stmt = first_child_type_node(child, "expr_stmt")
        elif child.type == "expr_stmt":
            expr_stmt = child
        else:
            continue

        if expr_stmt is None:
            continue
        if expr_stmt.children[0].type != "name":
            continue
        param = expr_stmt.children[0].value
        if not param.startswith("_"):
            continue
        value_node = expr_stmt.children[2]
        model_params[param] = get_node_value(value_node)
    return model_params


def _get_model_name(params) -> typing.Optional[str]:
    _name = params.get("_name")
    if _name:
        return _name
    _inherit = params.get("_inherit")
    if _inherit:
        if isinstance(_inherit, list):
            # `_inherit = []`
            if len(_inherit) == 0:
                return None
            # `_inherit = ['foo']`
            elif len(_inherit) == 1:
                return _inherit[0]
            # `_inherit = ['foo', 'bar', ...]`, currently not supported.
            else:
                raise ValueError(
                    f"Unexpected number of `_inherit` models: {len(_inherit)}"
                )
        else:
            return _inherit
    return None


class PythonEmitter(Check):
    _handles = {"addon_path"}
    _emits = {"python_module"}

    def on_addon_path(self, addon_path: AddonPath):
        if addon_path.path.suffix != ".py":
            return
        with addon_path.path.open(mode="rb") as f:
            module = get_parso_grammar(addon_path.addon.version).parse(f.read())
        yield PythonModule(addon_path.addon, addon_path.path, module)


class ModelDefinitionEmitter(Check):
    _handles = {"python_module"}
    _emits = {"model_definition"}

    def on_python_module(self, python_module: PythonModule):
        for classdef in python_module.module.iter_classdefs():
            model_params = _get_model_params(classdef)

            if not _get_model_name(model_params):
                continue

            yield ModelDefinition(
                addon=python_module.addon,
                path=python_module.path,
                node=classdef,
                class_name=classdef.name.value,
                params=model_params,
                bases=get_bases(classdef.get_super_arglist()),
            )


class FieldDefinitionEmitter(Check):
    _handles = {"model_definition"}
    _emits = {"field_definition"}

    def on_model_definition(self, model: ModelDefinition):
        field_types = FIELD_TYPE_VERSION_MAP[model.addon.version]
        for node in filter_child_nodes(model.node.get_suite(), "simple_stmt"):
            expr_stmt_node = first_child_type_node(node, "expr_stmt")
            if expr_stmt_node is None:
                continue

            if (
                expr_stmt_node.children[0].type == "name"
                and expr_stmt_node.children[1].type == "operator"
                and expr_stmt_node.children[2].type in ATOM_EXPR_NODE_TYPES
            ):
                field_name = expr_stmt_node.children[0].value

                # atom_expr
                field_node = expr_stmt_node.children[2]
                name_parts, leftover_nodes = consume_name(field_node)
                if not name_parts or len(name_parts) > 3 or len(leftover_nodes) != 1:
                    continue

                if len(name_parts) == 3 and (
                    name_parts[0] not in ("odoo", "openerp")
                    or name_parts[1] != "fields"
                ):
                    continue
                elif len(name_parts) == 2 and name_parts[0] != "fields":
                    continue

                field_class = name_parts[-1]

                # E.g. `foo = Someclass()``. Since we have no extra ways to
                # check if `Someclass` is a field, skip this case.
                if len(name_parts) == 1 and field_class not in field_types:
                    continue

                args, kwargs = [], []
                arg_node_list = []
                for child in leftover_nodes[0].children:
                    if child.type == "operator":
                        continue
                    elif child.type == "argument":
                        arg_node_list = [child]
                        break
                    elif child.type == "arglist":
                        arg_node_list = [
                            arg for arg in child.children if arg.type == "argument"
                        ]
                        break
                    else:
                        args.append(
                            FieldArg(
                                get_node_value(child), child.start_pos, child.end_pos
                            )
                        )

                for arg_node in arg_node_list:
                    if arg_node.children[0].type == "name":
                        kwarg_name = arg_node.children[0].value

                        if arg_node.children[2].type in STRING_NODE_TYPES:
                            kwarg_value = get_string_node_value(arg_node.children[2])
                        else:
                            kwarg_value = UNKNOWN

                        kwargs.append(
                            FieldKwarg(
                                name=kwarg_name,
                                value=kwarg_value,
                                start_pos=arg_node.start_pos,
                                end_pos=arg_node.end_pos,
                            )
                        )

                yield FieldDefinition(
                    name=field_name,
                    class_name=field_class,
                    model=model,
                    start_pos=field_node.start_pos,
                    end_pos=field_node.end_pos,
                    args=args,
                    kwargs=kwargs,
                )
