from odd.check import Check
from odd.issue import Issue, Location
from odd.xml_utils import get_view_arch, get_xpath_expr_target_element


class TreeString(Check):
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        model = xml_record.record_node.get("model")
        if model != "ir.ui.view":
            return

        arch = get_view_arch(xml_record.record_node)
        if arch is None:
            return
        for search in arch.xpath(".//tree[@string]"):
            yield Issue(
                "tree_view_string_attribute_deprecated",
                "`<tree>` `string` attribute is deprecated "
                "(no longer displayed) since version 8.0",
                xml_record.addon.manifest_path,
                [Location(xml_record.path, [search.sourceline])],
                categories=["maintainability", "deprecated"],
            )
        for xpath in arch.xpath('.//xpath[@position="attributes"]'):
            nodename = get_xpath_expr_target_element(xpath.get("expr"))
            if nodename != "tree":
                continue
            for attr in xpath.xpath('.//attribute[@name="string"]'):
                yield Issue(
                    "tree_view_string_attribute_deprecated",
                    "`<tree>` `string` attribute is deprecated "
                    "(no longer displayed) since version 8.0",
                    xml_record.addon.manifest_path,
                    [Location(xml_record.path, [attr.sourceline])],
                    categories=["maintainability", "deprecated"],
                )
