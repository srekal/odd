import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "search_string",
            [
                {
                    "slug": "search_view_element_takes_no_attributes",
                    "description": "`<search>` view element takes no attributes",
                    "locations": [(["views", "foo.xml"], [7])],
                    "categories": ["maintainability"],
                }
            ],
        )
    ],
)
def test_search_string(test_data_dir, addon_name, expected):
    run_check_test(test_data_dir, "search_string", ("__manifest__.py",), 12, expected)
