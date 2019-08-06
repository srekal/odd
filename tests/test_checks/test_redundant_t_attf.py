import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        ("double_braces", []),
        ("hashtag_brace", []),
        (
            "url_with_fragment",
            [
                {
                    "slug": "redundant_t_attf",
                    "description": (
                        "Element `<a>` has a redundant `t-attf-$name` attribute "
                        "`t-attf-href`: /web/login?redirect=1#login"
                    ),
                    "categories": ["correctness", "performance"],
                    "locations": [(["views", "website_templates.xml"], [5])],
                }
            ],
        ),
    ],
)
def test_redundant_t_attf(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir, "redundant_t_attf", (addon_name, "__manifest__.py"), 12, expected
    )
