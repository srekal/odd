from odin.checks import XMLCheck
from odin.issue import Issue, Location


class RedundantTAttf(XMLCheck):
    def check(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for template in tree.xpath("//template"):
            for el in template.xpath(".//*/@*[starts-with(name(), 't-attf-')]/.."):
                for name, value in el.attrib.iteritems():
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
                            addon.addon_path,
                            [Location(filename, [el.sourceline])],
                            categories=["correctness", "performance"],
                        )
