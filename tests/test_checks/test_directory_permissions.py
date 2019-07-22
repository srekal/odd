import pytest
from odin.addon import AddonPath
from odin.checks.addon import DirectoryPermissions
from odin.issue import Issue, Location
from odin.main import check_addon


def test_directory_permissions(test_data_dir):
    manifest_path = test_data_dir / "directory_permissions" / "__manifest__.py"
    issues = list(
        check_addon(
            manifest_path, {"directory_permissions": DirectoryPermissions}, version=12
        )
    )
    assert issues == [
        Issue(
            "directory_permissions",
            "Directories should have 755 permissions (current: 775)",
            AddonPath(manifest_path),
            [Location(manifest_path.parent / "views")],
            categories=["correctness"],
        )
    ]
