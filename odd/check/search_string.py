from odd.check import Check
from odd.issue import Issue, Location
from odd.xml_utils import get_view_arch, get_xpath_expr_target_element


class SearchString(Check):
    _handles = {"xml_record"}

    def _get_issue_from_element(self, addon, filename, element, attr_names):
        yield Issue(
            "search_view_element_takes_no_attributes",
            f"`<search>` view element takes no attributes, "
            f"has: {', '.join(attr_names)}",
            addon.manifest_path,
            [Location(filename, [element.sourceline])],
            categories=["maintainability"],
        )

    def on_xml_record(self, xml_record):
        arch = get_view_arch(xml_record.record_node)
        if arch is None:
            return
        for search in arch.iter("search"):
            if search.attrib:
                # Ignore extension.
                if len(search.attrib) == 1 and "position" in search.attrib:
                    continue
                yield from self._get_issue_from_element(
                    xml_record.addon, xml_record.path, search, search.attrib.keys()
                )

        for xpath in arch.xpath('.//xpath[@position="attributes"]'):
            nodename = get_xpath_expr_target_element(xpath.get("expr"))
            if nodename != "search":
                continue
            for attr in xpath.iterchildren(tag="attribute"):
                yield from self._get_issue_from_element(
                    xml_record.addon, xml_record.path, attr, [attr.get("name")]
                )
