import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "extra_content",
            12,
            [
                {
                    "slug": "relaxng_error",
                    "description": (
                        "XML file does not match Odoo RelaxNG schema: "
                        "Element odoo has extra content: record"
                    ),
                    "locations": [(["data", "foo.xml"], [(4, 1)])],
                    "categories": ["correctness"],
                }
            ],
        )
    ],
)
def test_relaxng(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir, "relaxng", (addon_name, "__manifest__.py"), version, expected
    )
