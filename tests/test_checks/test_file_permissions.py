from odin.addon import AddonPath
from odin.checks.addon import FilePermissions
from odin.issue import Issue, Location
from odin.main import check_addon


def test_file_permissions(test_data_dir):
    manifest_path = test_data_dir / "file_permissions" / "__manifest__.py"
    issues = list(
        check_addon(manifest_path, {"file_permissions": FilePermissions}, version=12)
    )
    assert issues == [
        Issue(
            "file_permissions",
            "Files should have 644 permissions (current: 664)",
            AddonPath(manifest_path),
            [Location(manifest_path)],
            categories=["correctness"],
        )
    ]
