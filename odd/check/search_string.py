from odd.check import Check
from odd.issue import Issue, Location
from odd.xmlutils import get_model_records, get_view_arch, get_xpath_expr_target_element


class SearchString(Check):
    def _get_issue_from_element(self, addon, filename, element, attr_names):
        yield Issue(
            "search_view_element_takes_no_attributes",
            f"`<search>` view element takes no attributes, "
            f"has: {', '.join(attr_names)}",
            addon.addon_path,
            [Location(filename, [element.sourceline])],
            categories=["maintainability"],
        )

    def on_xml_tree(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for record in get_model_records(tree, "ir.ui.view"):
            arch = get_view_arch(record)
            if arch is None:
                continue
            for search in arch.iter("search"):
                if search.attrib:
                    # Ignore extension.
                    if len(search.attrib) == 1 and "position" in search.attrib:
                        continue
                    yield from self._get_issue_from_element(
                        addon, filename, search, search.attrib.keys()
                    )

            for xpath in arch.xpath('.//xpath[@position="attributes"]'):
                nodename = get_xpath_expr_target_element(xpath.get("expr"))
                if nodename != "search":
                    continue
                for attr in xpath.iterchildren(tag="attribute"):
                    yield from self._get_issue_from_element(
                        addon, filename, attr, [attr.get("name")]
                    )
