import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "missing_closing_parenthesis_in_domain",
            [
                {
                    "slug": "invalid_eval_expression",
                    "description": (
                        'The Python expression in the "filter" element "domain" '
                        "attribute contains an error: SyntaxError: invalid syntax"
                    ),
                    "locations": [(["views", "foo.xml"], [9])],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("kanban_templates", []),
    ],
)
def test_xml_eval(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir, "xml_eval", (addon_name, "__manifest__.py"), 12, expected
    )
