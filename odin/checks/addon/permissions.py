from odin.checks import AddonCheck
from odin.issue import Issue, Location
from odin.utils import list_files

RECOMMENDED_FILE_PERMISSIONS = 0o644
RECOMMENDED_DIRECTORY_PERMISSIONS = 0o755


class FilePermissions(AddonCheck):
    def check(self, addon):
        for path in list_files(addon.path, list_dirs=True):
            if path.is_file():
                current_permissions = path.stat().st_mode & 0o777
                if current_permissions != RECOMMENDED_FILE_PERMISSIONS:
                    yield Issue(
                        "file_permissions",
                        f"Files should have {RECOMMENDED_FILE_PERMISSIONS:o} "
                        f"permissions (current: {current_permissions:o})",
                        addon.addon_path,
                        [Location(path)],
                        categories=["correctness"],
                    )


class DirectoryPermissions(AddonCheck):
    def check(self, addon):
        for path in list_files(addon.path, list_dirs=True):
            if path.is_dir():
                current_permissions = path.stat().st_mode & 0o777
                if current_permissions != RECOMMENDED_DIRECTORY_PERMISSIONS:
                    yield Issue(
                        "directory_permissions",
                        f"Directories should have {RECOMMENDED_DIRECTORY_PERMISSIONS:o} "
                        f"permissions (current: {current_permissions:o})",
                        addon.addon_path,
                        [Location(path)],
                        categories=["correctness"],
                    )
