from odin.addon import Addon
from odin.checks import FileCheck
from odin.issue import Issue, Location
from odin.xmlutils import get_root


class RedundantTAttf(FileCheck):
    def check(self, filename, addon: Addon):
        if filename.suffix.lower() != ".xml":
            return
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        root = get_root(filename)
        for template in root.xpath("//template"):
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
                            f"Element `<{el.tag}>` has a redundant `t-attf-$name` attribute `{name}`: {value}",
                            addon.addon_path,
                            [Location(filename, [el.sourceline])],
                            categories=["correctness", "performance"],
                        )
