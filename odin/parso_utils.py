import typing

import parso


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


def get_string_node_value(node: parso.python.tree.String) -> str:
    return node._get_payload()
