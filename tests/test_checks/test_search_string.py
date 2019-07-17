import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


def test_search_string(test_data_dir):
    manifest_path = test_data_dir / "search_string" / "__manifest__.py"
    addon_path = AddonPath(manifest_path)
    issues = list(check_addon(manifest_path, version=12))
    assert issues == [
        Issue(
            "search_view_element_takes_no_attributes",
            "`<search>` view element takes no attributes",
            addon_path,
            [Location(addon_path.path / "views/foo.xml", [7])],
            categories=["maintainability"],
        )
    ]
