from odd.check.base import Check
from odd.issue import Issue, Location


class AttributeOverride(Check):
    _handles = {"xml_tree"}

    def on_xml_tree(self, xml_tree):
        if xml_tree.addon.version < 9:
            return
        attributes = ", ".join(f'"{attr}"' for attr in ["class"])
        xpath = "|".join(
            f"/{main_tag}//attribute[@name=({attributes})]"
            for main_tag in ("openerp", "odoo")
        )
        for el in xml_tree.tree_node.xpath(xpath):
            is_override = not any(a in el.attrib for a in ("add", "remove"))
            if is_override:
                yield Issue(
                    "attribute_override",
                    f"`<attribute>` overrides the `{el.get('name')}` attribute value, "
                    f'consider using `add="..."` or `remove="..."` instead of '
                    f"overriding",
                    xml_tree.addon.manifest_path,
                    [Location(xml_tree.path, [el.sourceline])],
                    categories=["correctness", "maintainability"],
                )
