import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "noupdate_cron",
            [
                {
                    "slug": "expected_noupdate_flag",
                    "description": (
                        "`ir.cron` model records should be declared in a "
                        '`noupdate="1"` XML data section to allow user '
                        "modifications"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["data", "ir_cron.xml"], [5, 3])],
                }
            ],
        ),
        ("noupdate_cron_extension", []),
        ("noupdate_cron_odoo_1", []),
        (
            "noupdate_cron_odoo_0",
            [
                {
                    "slug": "expected_noupdate_flag",
                    "description": (
                        "`ir.cron` model records should be declared in a "
                        '`noupdate="1"` XML data section to allow user '
                        "modifications"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["data", "ir_cron.xml"], [5, 3])],
                }
            ],
        ),
    ],
)
def test_noupdate(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir, "noupdate", (addon_name, "__manifest__.py"), 12, expected
    )
