from odin.checks import XMLCheck
from odin.issue import Issue, Location
from odin.xmlutils import get_model_records, get_view_arch


class SearchString(XMLCheck):
    def check(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for record in get_model_records(tree, "ir.ui.view"):
            arch = get_view_arch(record)
            if arch is None:
                continue
            for search in arch.iter("search"):
                if search.attrib:
                    # Ignore extension.
                    if len(search.attrib) == 1 and "position" in search.attrib:
                        continue
                    yield Issue(
                        "search_view_element_takes_no_attributes",
                        "`<search>` view element takes no attributes",
                        addon.addon_path,
                        [Location(filename, [search.sourceline])],
                        categories=["maintainability"],
                    )
