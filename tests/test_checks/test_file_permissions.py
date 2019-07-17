from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


def test_file_permissions(test_data_dir):
    addon_path = test_data_dir / "file_permissions"
    issues = list(check_addon(addon_path / "__manifest__.py", version=12))
    assert issues == [
        Issue(
            "file_permissions",
            "Files should have 644 permissions (current: 664)",
            AddonPath(addon_path / "__manifest__.py"),
            [Location(addon_path / "__manifest__.py")],
            categories=["correctness"],
        )
    ]
