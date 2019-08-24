from odd.check import Check
from odd.issue import Issue, Location
from odd.utils import odoo_source_url
from odd.xml_utils import get_view_arch

CLASS_MAP = {"oe_highlight": "btn-primary", "oe_link": "btn-link"}


def _get_issues(xml_record, element, classes):
    classes = set((classes or "").split())
    for old_class, new_class in CLASS_MAP.items():
        if old_class in classes:
            yield Issue(
                "deprecated_button_class",
                f"`{old_class}` button class is deprecated since v12.0 "
                f"in favor of `{new_class}`",
                xml_record.addon.manifest_path,
                [Location(xml_record.path, [element.sourceline])],
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
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        if (
            xml_record.addon.version < 12
            or xml_record.record_node.get("model") != "ir.ui.view"
        ):
            return
        arch = get_view_arch(xml_record.record_node)
        if arch is None:
            return

        for button in arch.xpath(".//button"):
            if button.get("position"):
                continue
            yield from _get_issues(xml_record, button, button.get("class"))

        for attribute in arch.xpath(
            ".//button[@position='attributes']/attribute[@name='class']"
        ):
            yield from _get_issues(xml_record, attribute, attribute.text)
