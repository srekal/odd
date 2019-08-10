import typing
import ast
import dataclasses

import parso


UNKNOWN = object()


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
    if node.type == "string" or node.type == "strings":
        return get_string_node_value(node)
    else:
        if hasattr(node, "value"):
            return node.value
        else:
            try:
                return ast.literal_eval(node.get_code().strip())
            except ValueError:
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
    if node.type == "strings":
        return "".join(get_string_node_value(c) for c in node.children)
    return node._get_payload()


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
        return [_get_base(c) for c in node.children if c.type in ("name", "atom_expr")]
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
                else:
                    args.append(
                        FieldArg(get_node_value(child), child.start_pos, child.end_pos)
                    )

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
        from_names = ()
        if imp.type == "import_from":
            from_names = tuple(n.value for n in imp.get_from_names())
        names = tuple(n.value for path in imp.get_paths() for n in path)
        yield ModuleImport(imp.start_pos, imp.end_pos, from_names, names)
