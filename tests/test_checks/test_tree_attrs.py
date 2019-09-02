import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, addon_version, expected",
    [
        (
            "tree_string",
            12,
            [
                {
                    "slug": "deprecated_tree_attribute",
                    "description": (
                        "`<tree>` `string` attribute is deprecated since version 8.0"
                    ),
                    "locations": [(["views", "foo.xml"], [7])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        (
            "tree_string_xpath",
            12,
            [
                {
                    "slug": "deprecated_tree_attribute",
                    "description": (
                        "`<tree>` `string` attribute is deprecated since version 8.0"
                    ),
                    "locations": [(["views", "foo.xml"], [10])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        ("tree_string_deprecated_xml_not_included", 12, []),
        ("view_no_arch", 12, []),
        ("xpath_node_not_tree", 12, []),
        (
            "tree_colors",
            12,
            [
                {
                    "slug": "deprecated_tree_attribute",
                    "description": (
                        "`<tree>` `colors` attribute is deprecated since version 9.0"
                    ),
                    "locations": [(["views", "foo.xml"], [7])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        ("tree_colors_8", 8, []),
        (
            "tree_fonts",
            12,
            [
                {
                    "slug": "deprecated_tree_attribute",
                    "description": (
                        "`<tree>` `fonts` attribute is deprecated since version 9.0"
                    ),
                    "locations": [(["views", "foo.xml"], [7])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        ("tree_fonts_8", 8, []),
        (
            "tree_colors_xpath",
            12,
            [
                {
                    "slug": "deprecated_tree_attribute",
                    "description": (
                        "`<tree>` `colors` attribute is deprecated since version 9.0"
                    ),
                    "locations": [(["views", "foo.xml"], [10])],
                    "categories": ["deprecated"],
                }
            ],
        ),
    ],
)
def test_tree_attrs(test_data_dir, addon_name, addon_version, expected):
    run_check_test(
        test_data_dir,
        "tree_attrs",
        (addon_name, "__manifest__.py" if addon_version >= 10 else "__openerp__.py"),
        addon_version,
        expected,
    )
