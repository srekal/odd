from odd.check import Check
from odd.issue import Issue, Location

RECOMMENDED_FILE_PERMISSIONS = 0o644
RECOMMENDED_DIRECTORY_PERMISSIONS = 0o755


class FilePermissions(Check):
    _handles = {"addon_path"}

    def on_addon_path(self, addon_path):
        path = addon_path.path
        if path.is_file():
            current_permissions = path.stat().st_mode & 0o777
            if current_permissions != RECOMMENDED_FILE_PERMISSIONS:
                yield Issue(
                    "file_permissions",
                    f"Files should have {RECOMMENDED_FILE_PERMISSIONS:o} "
                    f"permissions (current: {current_permissions:o})",
                    addon_path.addon.manifest_path,
                    [Location(path)],
                    categories=["correctness"],
                )


class DirectoryPermissions(Check):
    _handles = {"addon_path"}

    def on_addon_path(self, addon_path):
        path = addon_path.path
        if path.is_dir():
            current_permissions = path.stat().st_mode & 0o777
            if current_permissions != RECOMMENDED_DIRECTORY_PERMISSIONS:
                yield Issue(
                    "directory_permissions",
                    f"Directories should have {RECOMMENDED_DIRECTORY_PERMISSIONS:o} "
                    f"permissions (current: {current_permissions:o})",
                    addon_path.addon.manifest_path,
                    [Location(path)],
                    categories=["correctness"],
                )
