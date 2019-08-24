from odd.check import Check
from odd.issue import Issue, Location


class RedundantTAttf(Check):
    _handles = {"xml_tree"}

    def on_xml_tree(self, xml_tree):
        for template in xml_tree.tree_node.xpath("//template"):
            for el in template.xpath(".//*/@*[starts-with(name(), 't-attf-')]/.."):
                for name, value in el.attrib.items():
                    if not name.startswith("t-attf-"):
                        continue

                    is_format_string = ("{{" in value and "}}" in value) or (
                        "#{" in value and "}" in value
                    )
                    if not is_format_string:
                        yield Issue(
                            "redundant_t_attf",
                            f"Element `<{el.tag}>` has a redundant `t-attf-$name` "
                            f"attribute `{name}`: {value}",
                            xml_tree.addon.manifest_path,
                            [Location(xml_tree.path, [el.sourceline])],
                            categories=["correctness", "performance"],
                        )
