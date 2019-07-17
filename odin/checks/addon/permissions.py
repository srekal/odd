from odin.checks import AddonCheck
from odin.issue import Issue, Location
from odin.utils import list_files


class FilePermissionsCheck(AddonCheck):
    def check(self, addon):
        for path in list_files(addon.path, list_dirs=True):
            if path.is_file():
                if path.stat().st_mode & 0o777 != 0o644:
                    yield Issue(
                        "file_permissions",
                        "Files should have 644 permissions",
                        addon.addon_path,
                        [Location(path)],
                        categories=["correctness"],
                    )


class DirectoryPermissionsCheck(AddonCheck):
    def check(self, addon):
        for path in list_files(addon.path, list_dirs=True):
            if path.is_dir():
                if path.stat().st_mode & 0o777 != 0o755:
                    yield Issue(
                        "directory_permissions",
                        "Directories should have 755 permissions",
                        addon.addon_path,
                        [Location(path)],
                        categories=["correctness"],
                    )
