from odin.checks import XMLCheck
from odin.issue import Issue, Location
from odin.xmlutils import (
    get_model_records,
    get_view_arch,
    get_xpath_expr_target_element,
)


class TreeString(XMLCheck):
    def check(self, addon, filename, tree):
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
                expr = xpath.get("expr")
                if not expr:
                    continue
                nodename = get_xpath_expr_target_element(expr)
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
