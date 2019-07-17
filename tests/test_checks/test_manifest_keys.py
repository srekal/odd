from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


def test_file_permissions(test_data_dir):
    manifest_path = test_data_dir / "manifest_keys" / "__manifest__.py"
    issues = list(check_addon(manifest_path, version=12))
    assert issues == [
        Issue(
            "unknown_manifest_key",
            'Unknown manifest key "foo"',
            AddonPath(manifest_path),
            [Location(manifest_path)],
            categories=["correctness"],
        )
    ]
