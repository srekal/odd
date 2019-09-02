from odd.check import Check
from odd.issue import Issue, Location


ELEMENTS = {"record", "template", "act_window", "menuitem", "report"}
XPATH_EXPR = "|".join(f"//{el}[not(@id)]" for el in ELEMENTS)


class XMLOperationNoID(Check):
    _handles = {"xml_tree"}

    def on_xml_tree(self, xml_tree):
        for el in xml_tree.tree_node.xpath(XPATH_EXPR):
            yield Issue(
                "xml_operation_without_id",
                f"XML operation `<{el.tag}>` has no `id` attribute",
                xml_tree.addon.manifest_path,
                [Location(xml_tree.path, [el.sourceline])],
                categories=["maintainability"],
            )
