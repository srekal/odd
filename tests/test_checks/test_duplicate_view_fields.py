import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "duplicate_inside_view",
            [
                {
                    "slug": "duplicate_view_field",
                    "description": (
                        '"foo_view_form" `ir.ui.view` has duplicate field "a"'
                    ),
                    "locations": [
                        (["views", "foo.xml"], [9]),
                        (["views", "foo.xml"], [11]),
                    ],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("embedded_view_no_duplicate", []),
        ("view_inherit", []),
        (
            "embedded_view_duplicate",
            [
                {
                    "slug": "duplicate_view_field",
                    "description": (
                        '"foo_view_form" `ir.ui.view` has duplicate field "name"'
                    ),
                    "locations": [
                        (["views", "foo.xml"], [16]),
                        (["views", "foo.xml"], [18]),
                    ],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("two_field_embedded_forms_no_duplicates", []),
        ("kanban_with_templates_no_duplicates", []),
        ("arch_override", []),
        ("no_arch", []),
        ("arch_two_children", []),
    ],
)
def test_duplicate_view_fields(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir,
        "duplicate_view_fields",
        (addon_name, "__manifest__.py"),
        12,
        expected,
    )
