import pytest
from odin.addon import AddonPath
from odin.checks.xml import TreeString
from odin.issue import Issue, Location
from odin.main import check_addon


def test_tree_string(test_data_dir):
    manifest_path = test_data_dir / "tree_string" / "tree_string" / "__manifest__.py"
    addon_path = AddonPath(manifest_path)
    issues = list(check_addon(manifest_path, {"tree_string": TreeString}, version=12))
    assert issues == [
        Issue(
            "tree_view_string_attribute_deprecated",
            "`<tree>` `string` attribute is deprecated (no longer displayed) since version 8.0",
            addon_path,
            [Location(addon_path.path / "views/foo.xml", [7])],
            categories=["maintainability", "deprecated"],
        )
    ]


def test_tree_string_xpath(test_data_dir):
    manifest_path = (
        test_data_dir / "tree_string" / "tree_string_xpath" / "__manifest__.py"
    )
    addon_path = AddonPath(manifest_path)
    issues = list(check_addon(manifest_path, {"tree_string": TreeString}, version=12))
    assert issues == [
        Issue(
            "tree_view_string_attribute_deprecated",
            "`<tree>` `string` attribute is deprecated (no longer displayed) since version 8.0",
            addon_path,
            [Location(addon_path.path / "views/foo.xml", [10])],
            categories=["maintainability", "deprecated"],
        )
    ]
