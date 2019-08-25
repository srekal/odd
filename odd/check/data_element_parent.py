from odd.check import Check
from odd.const import SUPPORTED_VERSIONS
from odd.issue import Issue, Location
from odd.utils import expand_version_list

ROOT_TAG_VERSION_MAP = expand_version_list(
    {">=8": ["openerp"], ">=9": ["odoo"]}, *SUPPORTED_VERSIONS, result_cls=list
)


class DataElementParent(Check):
    _handles = {"xml_tree"}

    def on_xml_tree(self, xml_tree):
        root_tags = ROOT_TAG_VERSION_MAP[xml_tree.addon.version]
        xpath_expr = "//data[%s]" % " and ".join(
            f"not(parent::{root_tag})" for root_tag in root_tags
        )

        for data in xml_tree.tree_node.xpath(xpath_expr):
            yield Issue(
                "invalid_data_element_parent",
                f"Expected `<data>` element to be a direct child of one of "
                f"these elements: {', '.join(root_tags)}",
                xml_tree.addon.manifest_path,
                [Location(xml_tree.path, [data.sourceline])],
                categories=["correctness"],
            )
