from odd.check import Check
from odd.issue import Issue, Location
from odd.xml_utils import get_view_arch, get_xpath_expr_target_element


class TreeAttrs(Check):
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        model = xml_record.record_node.get("model")
        if model != "ir.ui.view":
            return

        arch = get_view_arch(xml_record.record_node)
        if arch is None:
            return

        for attr, version in (("string", 8), ("colors", 9), ("fonts", 9)):
            if xml_record.addon.version < version:
                continue

            for search in arch.xpath(f".//tree[@{attr}]"):
                yield Issue(
                    "deprecated_tree_attribute",
                    f"`<tree>` `{attr}` attribute is deprecated since version "
                    f"{version}.0",
                    xml_record.addon.manifest_path,
                    [Location(xml_record.path, [search.sourceline])],
                    categories=["deprecated"],
                )
            for xpath in arch.xpath('.//xpath[@position="attributes"]'):
                nodename = get_xpath_expr_target_element(xpath.get("expr"))
                if nodename != "tree":
                    continue
                for attr_el in xpath.xpath(f'.//attribute[@name="{attr}"]'):
                    yield Issue(
                        "deprecated_tree_attribute",
                        f"`<tree>` `{attr}` attribute is deprecated since version "
                        f"{version}.0",
                        xml_record.addon.manifest_path,
                        [Location(xml_record.path, [attr_el.sourceline])],
                        categories=["deprecated"],
                    )
