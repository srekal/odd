import pathlib
import typing

from defusedxml import lxml

from odin.typedefs import Element, ElementGenerator


def get_root(xml_filename: pathlib.Path):
    with xml_filename.open(mode="rb") as f:
        return lxml.parse(f).getroot()


def get_records(root: Element) -> ElementGenerator:
    for child in root:
        if child.tag == "data":
            yield from get_records(child)
        else:
            yield child


def get_model_records(root: Element, model: str) -> ElementGenerator:
    for el in get_records(root):
        if el.tag == "record":
            if el.get("model") == model:
                yield el


def get_view_arch(record: Element) -> typing.Optional[Element]:
    for field in record.iter("field"):
        if field.get("name") == "arch":
            return field
