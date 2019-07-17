import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


def test_directory_permissions(test_data_dir):
    addon_path = test_data_dir / "directory_permissions"
    issues = list(check_addon(addon_path / "__manifest__.py", version=12))
    assert issues == [
        Issue(
            "directory_permissions",
            "Directories should have 755 permissions",
            AddonPath(addon_path / "__manifest__.py"),
            [Location(addon_path / "views")],
            categories=["correctness"],
        )
    ]
