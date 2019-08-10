from odd.check import Check
from odd.issue import Issue, Location
from odd.utils import list_files, lookup_version_list

EXT_VERSION_MAP = {">=8": ["csv", "xml", "sql"], ">=8,<12": ["yml"]}


class DataFileInclusion(Check):
    def on_before(self, addon):
        extensions = {
            f".{ext}" for ext in lookup_version_list(EXT_VERSION_MAP, addon.version)
        }
        combined_data_files = {*addon.data_files, *addon.demo_files, *addon.qweb_files}
        exclude_dirs = {addon.path / dir for dir in ("tests", "static/src/xml")}

        for file_path in list_files(
            addon.path, list_dirs=False, exclude_dirs=exclude_dirs
        ):
            if file_path.suffix not in extensions:
                continue
            if file_path not in combined_data_files:
                yield Issue(
                    "data_file_missing_in_manifest",
                    "Data file is not included in `demo` or `data` "
                    "sections in the manifest file",
                    addon.addon_path,
                    [Location(file_path)],
                    categories=["correctness"],
                )
