import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "tree_string",
            [
                {
                    "slug": "tree_view_string_attribute_deprecated",
                    "description": "`<tree>` `string` attribute is deprecated (no longer displayed) since version 8.0",
                    "locations": [(["views", "foo.xml"], [7])],
                    "categories": ["maintainability", "deprecated"],
                }
            ],
        ),
        (
            "tree_string_xpath",
            [
                {
                    "slug": "tree_view_string_attribute_deprecated",
                    "description": "`<tree>` `string` attribute is deprecated (no longer displayed) since version 8.0",
                    "locations": [(["views", "foo.xml"], [10])],
                    "categories": ["maintainability", "deprecated"],
                }
            ],
        ),
    ],
)
def test_tree_string(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir, "tree_string", (addon_name, "__manifest__.py"), 12, expected
    )
