from odin.checks import FileCheck
from odin.issue import Issue, Location
from odin.xmlutils import get_root


class AttributeOverride(FileCheck):
    def check(self, filename, addon):
        if addon.version < 9 or filename.suffix.lower() != ".xml":
            return
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        root = get_root(filename)
        attributes = ", ".join(f'"{attr}"' for attr in ["class"])
        xpath = "|".join(
            f"/{main_tag}//attribute[@name=({attributes})]"
            for main_tag in ("openerp", "odoo")
        )
        for el in root.xpath(xpath):
            is_override = not any(a in el.attrib for a in ("add", "remove"))
            if is_override:
                yield Issue(
                    "attribute_override",
                    f"`<attribute>` overrides the `{el.get('name')}` attribute value, consider using `add=\"...\"` or `remove=\"...\"` instead of overriding",
                    addon.addon_path,
                    [Location(filename, [el.sourceline])],
                    categories=["correctness", "maintainability"],
                )
