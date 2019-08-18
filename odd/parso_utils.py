import typing
import ast
import dataclasses

import parso

from odd.addon import Addon
from odd.const import UNKNOWN

STRING_NODE_TYPES = frozenset(("string", "strings"))
ATOM_EXPR_NODE_TYPES = frozenset(("atom_expr", "power"))  # "power" is PY2.


class Position(typing.NamedTuple):
    line: int
    column: int


@dataclasses.dataclass
class ModuleImport:
    start_pos: Position
    end_pos: Position
    from_names: typing.Tuple[str, ...] = dataclasses.field(default_factory=tuple)
    names: typing.Tuple[str, ...] = dataclasses.field(default_factory=tuple)


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
    class_name: str
    params: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
    bases: typing.List = dataclasses.field(default_factory=list)
    fields: typing.List[Field] = dataclasses.field(default_factory=list)

    @property
    def name(self):
        return self.params.get("_name") or self.params.get("_inherit")


@dataclasses.dataclass
class Call:
    names: typing.Tuple[str, ...]
    args: typing.Tuple[typing.Any, ...]
    kwargs: typing.Dict[str, typing.Any]
    start_pos: Position
    end_pos: Position


def iter_calls(main_node: parso.tree.NodeOrLeaf) -> typing.Generator[Call, None, None]:
    for node in walk(main_node):
        if node.type not in ATOM_EXPR_NODE_TYPES:
            continue
        yield from _parse_call(node)


def parse_call_args(
    arg_nodes: typing.Iterable[parso.tree.NodeOrLeaf],
) -> typing.Tuple[typing.Tuple[typing.Any, ...], typing.Dict[str, typing.Any]]:
    args, kwargs = [], {}

    def parse_argument(arg_node):
        if is_string_node(arg_node):
            args.append(get_string_node_value(arg_node))
        elif arg_node.type in ("number", "keyword"):
            args.append(get_node_value(arg_node))
        elif arg_node.type == "name":
            args.append(UNKNOWN)
        elif arg_node.type == "operator" and arg_node.value == ",":
            ...
        elif (
            isinstance(arg_node, parso.tree.Node)
            and len(arg_node.children) == 2
            and arg_node.children[0].type == "operator"
            and arg_node.children[0].value in ("*", "**")
            and arg_node.children[1].type == "name"
        ):
            # *a, **kw
            ...
        elif (
            isinstance(arg_node, parso.tree.Node)
            and len(arg_node.children) == 3
            and arg_node.children[0].type == "name"
            and arg_node.children[1].type == "operator"
            and arg_node.children[1].value == "="
        ):
            name, op, value_node = arg_node.children
            kwargs[name.value] = get_node_value(value_node)
        else:
            # print(f"Unexpected args: {arg_node!r}")
            args.append(UNKNOWN)

    for arg_node in arg_nodes:
        if arg_node.type == "arglist":
            for child_arg in arg_node.children:
                parse_argument(child_arg)
        else:
            parse_argument(arg_node)

    return tuple(args), kwargs


def _parse_call(node: parso.tree.Node) -> typing.Generator[Call, None, None]:
    name_parts = []
    for child in node.children:
        if child.type == "name":
            name_parts.append(child.value)
        elif child.type == "trailer":
            if not child.children:
                continue

            if is_parenthesized(child):
                args, kwargs = parse_call_args(child.children[1:-1])
                yield Call(
                    tuple(name_parts), args, kwargs, child.start_pos, child.end_pos
                )
                continue

            for sub_child in child.children:
                if sub_child.type == "operator" and sub_child.value == ".":
                    ...
                elif sub_child.type == "name":
                    name_parts.append(sub_child.value)
                else:
                    ...
                    # print(f"Unhandled subchild: {sub_child!r}")
        else:
            ...
            # print(f"Unexpected node while parsing call: {child!r}")


def get_parso_grammar(addon: Addon) -> parso.Grammar:
    return parso.load_grammar(version="2.7" if addon.version < 11 else "3.5")


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


def column_index_1(position: typing.Tuple[int, int]) -> typing.Tuple[int, int]:
    return position[0], position[1] + 1


def filter_child_nodes(node: parso.tree.Node, *types: str):
    unique_types = set(types)
    for child_node in node.children:
        if child_node.type in unique_types:
            yield child_node


def first_child_type_node(node: parso.python.tree.Node, type: str):
    return next(filter_child_nodes(node, type), None)


def get_node_value(node: parso.tree.NodeOrLeaf) -> typing.Any:
    if is_string_node(node):
        return get_string_node_value(node)
    elif node.type == "keyword" and node.value in ("True", "False"):
        return node.value == "True"
    elif node.type == "numeric":
        return ast.literal_eval(node.value)
    else:
        if hasattr(node, "value"):
            return node.value
        else:
            try:
                return ast.literal_eval(node.get_code().strip())
            except (SyntaxError, ValueError, IndentationError):
                return UNKNOWN


def get_model_params(
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


def extract_func_name(node: parso.tree.NodeOrLeaf) -> typing.List[str]:
    name_parts = []
    for child in walk(node):
        if child.type == "operator" and child.value == "(":
            break
        elif child.type == "name":
            name_parts.append(child.value)
    return name_parts


def get_string_node_value(node: parso.tree.NodeOrLeaf) -> str:
    if node.type in ("strings", "arith_expr", "atom"):
        if node.type == "arith_expr":
            children = node.children[::2]
        elif node.type == "atom":
            children = node.children[1:-1]
        else:
            children = node.children
        return "".join(get_string_node_value(child) for child in children)
    elif node.type == "string":
        return node._get_payload()
    else:
        raise TypeError(f"Unexpected node type: {node.type}")


def is_string_arith_expr(node: parso.tree.NodeOrLeaf) -> bool:
    """Returns True if `node` is `"a" + [... +] "z"`."""
    if node.type != "arith_expr":
        return False

    if len(node.children) % 2 != 1:
        return False

    for string_node in node.children[::2]:
        if string_node.type not in STRING_NODE_TYPES:
            return False

    for op_node in node.children[1::2]:
        if op_node.type != "operator" or op_node.value != "+":
            return False

    return True


def is_parenthesized(node: parso.tree.Node) -> bool:
    if len(node.children) < 2:
        return False
    head, tail = node.children[0], node.children[-1]
    return (
        head.type == "operator"
        and tail.type == "operator"
        and head.value == "("
        and tail.value == ")"
    )


def is_string_atom(node: parso.tree.NodeOrLeaf) -> bool:
    """Returns True if `node` is `("a" [...] "z")`."""
    if node.type != "atom":
        return False

    if not is_parenthesized(node):
        return False

    for child in node.children[1:-1]:
        if child.type not in STRING_NODE_TYPES:
            return False

    return True


def is_string_node(node: parso.tree.NodeOrLeaf) -> bool:
    return (
        node.type in STRING_NODE_TYPES
        or is_string_arith_expr(node)
        or is_string_atom(node)
    )


def _get_base(node: parso.tree.NodeOrLeaf) -> typing.Tuple[str, ...]:
    name_parts = []
    for child in [node] if node.type == "name" else node.children:
        if child.type == "operator" and child.value == ".":
            continue
        elif child.type == "name":
            name_parts.append(str(child.value))
        elif child.type == "trailer":
            name_parts.extend(_get_base(child))
        else:
            raise ValueError(f"Unexpected node type: {child.type}")
    return tuple(name_parts)


def get_bases(
    node: typing.Optional[parso.tree.NodeOrLeaf]
) -> typing.List[typing.Tuple[str, ...]]:
    if node is None:
        return []
    elif node.type == "arglist" or node.type == "testlist":
        return [
            _get_base(c)
            for c in node.children
            if c.type == "name" or c.type in ATOM_EXPR_NODE_TYPES
        ]
    else:
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
            and expr_stmt_node.children[2].type in ATOM_EXPR_NODE_TYPES
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
                else:
                    args.append(
                        FieldArg(get_node_value(child), child.start_pos, child.end_pos)
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

    model_params = get_model_params(classdef_node)

    model = Model(
        class_name=classdef_node.name.value,
        params=model_params,
        bases=get_bases(classdef_node.get_super_arglist()),
    )

    if extract_fields:
        for field in _get_model_fields(classdef_node.get_suite()):
            model.fields.append(field)

    return model


def get_model_type(classdef_node) -> typing.Union[str, object]:
    bases = get_bases(classdef_node.get_super_arglist())
    for type_, class_ in [
        ("model", "Model"),
        ("transient", "TransientModel"),
        ("abstract", "AbstractModel"),
    ]:
        if (
            (class_,) in bases
            or ("models", class_) in bases
            or ("odoo", "models", class_) in bases
            or ("openerp", "models", class_) in bases
        ):
            return type_
    return UNKNOWN


def get_imports(module) -> typing.Generator[ModuleImport, None, None]:
    for imp in module.iter_imports():
        if imp.type == "import_from":
            from_names = tuple(n.value for n in imp.get_from_names())
        else:
            from_names = ()
        names = tuple(n.value for path in imp.get_paths() for n in path)
        yield ModuleImport(imp.start_pos, imp.end_pos, from_names, names)
