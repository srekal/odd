import pathlib
import typing
import re

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


def get_model_records(
    root: Element, model: typing.Optional[str] = None
) -> ElementGenerator:
    for el in get_records(root):
        if el.tag == "record":
            if not model or el.get("model") == model:
                yield el


def get_view_arch(record: Element) -> typing.Optional[Element]:
    for field in record.iter("field"):
        if field.get("name") == "arch":
            return field


def get_xpath_expr_target_element(xpath_expr: str) -> typing.Optional[str]:
    last_part = xpath_expr.split("/")[-1]
    m = re.search(r"(?P<modifier>[^:]+::)?(?<!@)(?P<nodename>[^\[]+)", last_part)
    nodename = None
    if m is not None:
        nodename = m.group("nodename")
    if nodename == ".":
        nodename = None
    return nodename


def split_xml_id(xml_id: str) -> typing.Tuple[typing.Optional[str], str]:
    if "." in xml_id:
        return xml_id.split(".")
    return None, xml_id
