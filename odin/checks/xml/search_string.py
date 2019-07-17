import pathlib

from odin.addon import Addon
from odin.checks import FileCheck
from odin.issue import Issue, Location
from odin.xmlutils import get_model_records, get_root, get_view_arch


class SearchString(FileCheck):
    def check(self, filename: pathlib.Path, addon: Addon):
        if filename.suffix.lower() != ".xml":
            return
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for record in get_model_records(get_root(filename), "ir.ui.view"):
            arch = get_view_arch(record)
            if arch is None:
                continue
            for search in arch.iter("search"):
                if search.attrib:
                    yield Issue(
                        "search_view_element_takes_no_attributes",
                        "`<search>` view element takes no attributes",
                        addon.addon_path,
                        [Location(filename, [search.sourceline])],
                        categories=["maintainability"],
                    )
