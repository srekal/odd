from odd.check import Check
from odd.issue import Issue, Location
from odd.utils import odoo_source_url
from odd.xml_utils import get_model_records, get_view_arch

CLASS_MAP = {"oe_highlight": "btn-primary", "oe_link": "btn-link"}


def _get_issues(addon, filename, element, classes):
    classes = set((classes or "").split())
    for old_class, new_class in CLASS_MAP.items():
        if old_class in classes:
            yield Issue(
                "deprecated_button_class",
                f"`{old_class}` button class is deprecated since v12.0 "
                f"in favor of `{new_class}`",
                addon.addon_path,
                [Location(filename, [element.sourceline])],
                categories=["maintainability", "deprecated"],
                sources=[
                    odoo_source_url(
                        "1e5fbb8e5bf0e0458d83a399b2b59d03a601e86a",
                        "addons/web/static/src/js/core/dom.js",
                        start=340,
                        end=345,
                    )
                ],
            )


class ButtonClasses(Check):
    def on_xml_tree(self, addon, filename, tree):
        if addon.version < 12 or (
            filename not in addon.data_files and filename not in addon.demo_files
        ):
            return
        for record in get_model_records(tree, "ir.ui.view"):
            arch = get_view_arch(record)
            if arch is None:
                continue

            for button in arch.xpath(".//button"):
                if button.get("position"):
                    continue
                yield from _get_issues(addon, filename, button, button.get("class"))

            for attribute in arch.xpath(
                ".//button[@position='attributes']/attribute[@name='class']"
            ):
                yield from _get_issues(addon, filename, attribute, attribute.text)
