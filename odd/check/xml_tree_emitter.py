import dataclasses
import logging
import typing

from odd.check import Check
from odd.check.path_emitter import AddonPath
from odd.xml_utils import get_root

_LOG = logging.getLogger(__name__)


def is_noupdate(record_node) -> bool:
    parent = record_node.getparent()
    if parent is None:
        _LOG.warning("Element <%s> has no parent tag", record_node.tag)
        return False

    # TODO: Limit tags based on addon version (e.g. no `odoo` in v8).
    if parent.tag not in ("data", "odoo", "openerp"):
        raise ValueError(f"Unexpected <record> parent tag: {parent.tag}")
    if "noupdate" in parent.attrib:
        return (parent.get("noupdate") or "").lower() in ("1", "true")
    else:
        if parent.tag == "data":
            return is_noupdate(parent)
        else:
            return False


@dataclasses.dataclass
class XMLTree(AddonPath):
    tree_node: typing.Any  # TODO: Need a type for `lxml` tree.


@dataclasses.dataclass
class XMLRecord(AddonPath):
    record_node: typing.Any  # TODO: Need a type.
    noupdate: bool


class XMLTreeEmitter(Check):
    _handles = {"data_file", "demo_file", "xml_tree"}
    _emits = {"xml_tree", "xml_record"}

    def _load_tree(self, addon_path):
        if addon_path.path.suffix.lower() == ".xml":
            yield XMLTree(addon_path.addon, addon_path.path, get_root(addon_path.path))

    def on_data_file(self, addon_path):
        yield from self._load_tree(addon_path)

    def on_demo_file(self, addon_path):
        yield from self._load_tree(addon_path)

    def on_xml_tree(self, xml_tree):
        # TODO: Use more precise XPath expressions, e.g. `//odoo/data/record`,
        # based also on addon version.
        for record_node in xml_tree.tree_node.xpath("//record"):
            yield XMLRecord(
                xml_tree.addon, xml_tree.path, record_node, is_noupdate(record_node)
            )
