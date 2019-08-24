import collections
import pathlib
import typing

from odd.utils import Position

import yaml


class YamlTag(collections.abc.Mapping):
    def __init__(self, tag, start_pos, end_pos, **kwargs):
        self.tag = tag
        self.start_pos, self.end_pos = start_pos, end_pos
        self._kwargs = kwargs

    def __getitem__(self, key):
        return self._kwargs[key]

    def __iter__(self):
        return iter(self._kwargs)

    def __len__(self):
        return len(self._kwargs)

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return f"<!{self.tag} {sorted(self.items())}>"


def line_column_index_1(position: Position) -> Position:
    return Position(position[0] + 1, position[1] + 1)


def _get_positions(node) -> typing.Tuple[Position, Position]:
    return (
        Position(node.start_mark.line, node.start_mark.column),
        Position(node.end_mark.line, node.end_mark.column),
    )


def assert_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("assert", *_get_positions(node), **kwargs)


def record_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("record", *_get_positions(node), **kwargs)


def python_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("python", *_get_positions(node), **kwargs)


def menuitem_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("menuitem", *_get_positions(node), **kwargs)


def workflow_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("workflow", *_get_positions(node), **kwargs)


def act_window_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("act_window", *_get_positions(node), **kwargs)


def function_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("function", *_get_positions(node), **kwargs)


def report_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("report", *_get_positions(node), **kwargs)


def delete_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("delete", *_get_positions(node), **kwargs)


def context_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("context", *_get_positions(node), **kwargs)


def url_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("url", *_get_positions(node), **kwargs)


def eval_constructor(loader, node):
    expression = loader.construct_scalar(node)
    return YamlTag("eval", *_get_positions(node), expression=expression)


def ref_constructor(loader, tag_suffix, node):
    if tag_suffix == "id":
        kwargs = {"id": loader.construct_scalar(node)}
    else:
        kwargs = loader.construct_mapping(node)
    return YamlTag("ref", *_get_positions(node), **kwargs)


def ir_set_constructor(loader, node):
    kwargs = loader.construct_mapping(node)
    return YamlTag("ir_set", *_get_positions(node), **kwargs)


def add_constructors():
    yaml.add_constructor("!assert", assert_constructor)
    yaml.add_constructor("!record", record_constructor)
    yaml.add_constructor("!python", python_constructor)
    yaml.add_constructor("!menuitem", menuitem_constructor)
    yaml.add_constructor("!workflow", workflow_constructor)
    yaml.add_constructor("!act_window", act_window_constructor)
    yaml.add_constructor("!function", function_constructor)
    yaml.add_constructor("!report", report_constructor)
    yaml.add_constructor("!context", context_constructor)
    yaml.add_constructor("!delete", delete_constructor)
    yaml.add_constructor("!url", url_constructor)
    yaml.add_constructor("!eval", eval_constructor)
    yaml.add_multi_constructor("!ref", ref_constructor)
    yaml.add_constructor("!ir_set", ir_set_constructor)


def load(path: pathlib.Path) -> typing.Any:
    add_constructors()
    with path.open(mode="rb") as f:
        return yaml.load(f, Loader=yaml.Loader)
