import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


def test_tree_string(test_data_dir):
    addon_path = test_data_dir / "tree_string"
    issues = list(check_addon(addon_path, version=12))
    assert issues == [
        Issue(
            "tree_view_string_attribute_deprecated",
            "`<tree>` `string` attribute is deprecated (no longer displayed) since version 8.0",
            AddonPath(addon_path / "__manifest__.py"),
            [Location(addon_path / "views/foo.xml", [7])],
            categories=["maintainability", "deprecated"],
        )
    ]
