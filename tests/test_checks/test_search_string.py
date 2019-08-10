import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "string_attr",
            [
                {
                    "slug": "search_view_element_takes_no_attributes",
                    "description": (
                        "`<search>` view element takes no attributes, " "has: string"
                    ),
                    "locations": [(["views", "foo.xml"], [7])],
                    "categories": ["maintainability"],
                }
            ],
        ),
        (
            "attr_added_via_xpath",
            [
                {
                    "slug": "search_view_element_takes_no_attributes",
                    "description": (
                        "`<search>` view element takes no attributes, " "has: string"
                    ),
                    "locations": [(["views", "foo.xml"], [10])],
                    "categories": ["maintainability"],
                }
            ],
        ),
        ("attr_added_via_xpath_node_not_search", []),
        ("view_extension", []),
        ("string_attr_xml_not_included", []),
        ("no_string_attr", []),
        ("view_no_arch", []),
    ],
)
def test_search_string(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir, "search_string", (addon_name, "__manifest__.py"), 12, expected
    )
