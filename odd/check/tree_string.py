from odd.check import Check
from odd.issue import Issue, Location
from odd.xmlutils import get_model_records, get_view_arch, get_xpath_expr_target_element


class TreeString(Check):
    def on_xml_tree(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for record in get_model_records(tree, "ir.ui.view"):
            arch = get_view_arch(record)
            if arch is None:
                continue
            for search in arch.iter("tree"):
                if "string" in search.attrib:
                    yield Issue(
                        "tree_view_string_attribute_deprecated",
                        "`<tree>` `string` attribute is deprecated "
                        "(no longer displayed) since version 8.0",
                        addon.addon_path,
                        [Location(filename, [search.sourceline])],
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
                        addon.addon_path,
                        [Location(filename, [attr.sourceline])],
                        categories=["maintainability", "deprecated"],
                    )
