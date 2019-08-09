from odd.check.base import Check
from odd.issue import Issue, Location


class AttributeOverride(Check):
    def on_xml_tree(self, addon, filename, tree):
        if addon.version < 9 or (
            filename not in addon.data_files and filename not in addon.demo_files
        ):
            return
        attributes = ", ".join(f'"{attr}"' for attr in ["class"])
        xpath = "|".join(
            f"/{main_tag}//attribute[@name=({attributes})]"
            for main_tag in ("openerp", "odoo")
        )
        for el in tree.xpath(xpath):
            is_override = not any(a in el.attrib for a in ("add", "remove"))
            if is_override:
                yield Issue(
                    "attribute_override",
                    f"`<attribute>` overrides the `{el.get('name')}` attribute value, "
                    f'consider using `add="..."` or `remove="..."` instead of '
                    f"overriding",
                    addon.addon_path,
                    [Location(filename, [el.sourceline])],
                    categories=["correctness", "maintainability"],
                )
