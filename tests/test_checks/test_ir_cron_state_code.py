import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "code_set_state_omitted",
            12,
            [
                {
                    "slug": "incorrect_cron_record",
                    "description": (
                        '`ir.cron` record "foo_cron_compute_pi" has `code` set, '
                        "but no `state` set - code will not be executed when the "
                        "cron job runs"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["data", "ir_cron.xml"], [7])],
                }
            ],
        ),
        ("code_set_state_omitted_v10", 10, []),
        (
            "code_set_state_is_not_code",
            12,
            [
                {
                    "slug": "incorrect_cron_record",
                    "description": (
                        '`ir.cron` record "foo_cron_compute_pi" has `code` set, '
                        'but `state` is not "code" - code will not be executed when '
                        "the cron job runs"
                    ),
                    "categories": ["correctness"],
                    "locations": [
                        (["data", "ir_cron.xml"], [7]),
                        (["data", "ir_cron.xml"], [8]),
                    ],
                }
            ],
        ),
        (
            "state_is_code_but_code_not_set",
            12,
            [
                {
                    "slug": "incorrect_cron_record",
                    "description": (
                        '`ir.cron` record "foo_cron_compute_pi" has `state` set to '
                        '"code", but `code` is not set'
                    ),
                    "categories": ["correctness"],
                    "locations": [(["data", "ir_cron.xml"], [7])],
                }
            ],
        ),
    ],
)
def test_ir_cron_state_code(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "ir_cron_state_code",
        (addon_name, "__manifest__.py" if version >= 10 else "__openerp__.py"),
        version,
        expected,
    )
