import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


def test_search_string(test_data_dir):
    addon_path = test_data_dir / "search_string"
    issues = list(check_addon(addon_path, version=12))
    assert issues == [
        Issue(
            "search_view_element_takes_no_attributes",
            "`<search>` view element takes no attributes",
            AddonPath(addon_path / "__manifest__.py"),
            [Location(addon_path / "views/foo.xml", [7])],
            categories=["maintainability"],
        )
    ]
