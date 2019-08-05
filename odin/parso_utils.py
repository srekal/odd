import typing
import ast
import dataclasses

import parso


UNKNOWN = object()


class Position(typing.NamedTuple):
    line: int
    column: int


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
class Field:
    name: str
    class_name: str
    start_pos: Position
    end_pos: Position
    args: typing.List[FieldArg] = dataclasses.field(default_factory=list)
    kwargs: typing.List[FieldKwarg] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Model:
    name: str
    class_name: str
    bases: typing.Set = dataclasses.field(default_factory=set)
    fields: typing.List[Field] = dataclasses.field(default_factory=list)


def walk(
    node: parso.tree.NodeOrLeaf
) -> typing.Generator[parso.tree.NodeOrLeaf, None, None]:
    yield node
    try:
        children = node.children
    except AttributeError:
        pass
    else:
        for child in children:
            yield from walk(child)


def filter_child_nodes(node: parso.tree.Node, *types: str):
    types = set(types)
    for child_node in node.children:
        if child_node.type in types:
            yield child_node


def first_child_type_node(node: parso.python.tree.Node, type: str):
    return next(filter_child_nodes(node, type), None)


def get_model_name(classdef_node: parso.python.tree.Class) -> typing.Optional[str]:
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


def extract_func_name(node: parso.tree.NodeOrLeaf) -> typing.List[str]:
    name_parts = []
    for child in walk(node):
        if child.type == "operator" and child.value == "(":
            break
        elif child.type == "name":
            name_parts.append(child.value)
    return name_parts


def get_string_node_value(node: parso.tree.Node) -> str:
    if node.type == "strings":
        return "".join(get_string_node_value(c) for c in node.children)
    return node._get_payload()


def _get_base(node) -> typing.Tuple[str]:
    name_parts = []
    for child in [node] if node.type == "name" else node.children:
        if child.type == "operator" and child.value == ".":
            continue
        elif child.type == "name":
            name_parts.append(child.value)
        elif child.type == "trailer":
            name_parts.extend(_get_base(child))
        else:
            raise ValueError(f"Unexpected node type: {child.type}")
    return tuple(name_parts)


def get_bases(node) -> typing.List[typing.Tuple[str]]:
    if node.type == "arglist":
        return [_get_base(c) for c in node.children if c.type in ("name", "atom_expr")]
    return [_get_base(node)]


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


def _get_model_fields(suite):
    for node in filter_child_nodes(suite, "simple_stmt"):
        expr_stmt_node = first_child_type_node(node, "expr_stmt")
        if expr_stmt_node is None:
            continue

        if (
            expr_stmt_node.children[0].type == "name"
            and expr_stmt_node.children[1].type == "operator"
            and expr_stmt_node.children[2].type in ("atom_expr", "power")
        ):
            field_name = expr_stmt_node.children[0].value

            # atom_expr
            field_node = expr_stmt_node.children[2]
            name_parts, leftover_nodes = consume_name(field_node)
            if not name_parts or len(name_parts) > 3 or len(leftover_nodes) != 1:
                continue

            if len(name_parts) == 3 and (
                name_parts[0] not in ("odoo", "openerp") or name_parts[1] != "fields"
            ):
                continue
            elif len(name_parts) == 2 and name_parts[0] != "fields":
                continue

            field_class = name_parts[-1]
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
                elif child.type == "string" or child.type == "strings":
                    args.append(
                        FieldArg(
                            get_string_node_value(child), child.start_pos, child.end_pos
                        )
                    )
                else:
                    if hasattr(child, "value"):
                        arg_value = child.value
                    else:
                        try:
                            arg_value = ast.literal_eval(child.get_code())
                        except ValueError:
                            arg_value = UNKNOWN
                    args.append(FieldArg(arg_value, child.start_pos, child.end_pos))

            for arg_node in arg_node_list:
                if arg_node.children[0].type == "name":
                    kwarg_name = arg_node.children[0].value

                    if arg_node.children[2].type in ("string", "strings"):
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

            yield Field(
                name=field_name,
                class_name=field_class,
                start_pos=field_node.start_pos,
                end_pos=field_node.end_pos,
                args=args,
                kwargs=kwargs,
            )


def get_model_definition(classdef_node, *, extract_fields: bool = True):
    assert classdef_node.type == "classdef"

    model_name = get_model_name(classdef_node)
    if model_name is None:
        return

    model = Model(
        name=model_name,
        class_name=classdef_node.name.value,
        bases=get_bases(classdef_node.get_super_arglist()),
    )

    if extract_fields:
        for field in _get_model_fields(classdef_node.get_suite()):
            model.fields.append(field)

    return model
