import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "not_tagged",
            12,
            [
                {
                    "slug": "unittest_testcase_not_tagged",
                    "description": (
                        "`unittest.TestCase` subclass `TestFoo` is not decorated with "
                        "`@tagged()`, it will not be picked up by Odoo test runner"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["tests", "test_foo.py"], [(4, 1)])],
                    "sources": [
                        "https://github.com/odoo/odoo/commit/"
                        "b356b190338e3ee032b9e3a7f670f76468965006"
                    ],
                }
            ],
        ),
        (
            "not_tagged_direct_import",
            12,
            [
                {
                    "slug": "unittest_testcase_not_tagged",
                    "description": (
                        "`unittest.TestCase` subclass `TestFoo` is not decorated with "
                        "`@tagged()`, it will not be picked up by Odoo test runner"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["tests", "test_foo.py"], [(4, 1)])],
                    "sources": [
                        "https://github.com/odoo/odoo/commit/"
                        "b356b190338e3ee032b9e3a7f670f76468965006"
                    ],
                }
            ],
        ),
        ("not_tagged_11", 11, []),
        ("tagged", 12, []),
        ("not_tagged_not_a_test_case", 12, []),
    ],
)
def test_unittest_testcase_tagged(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "unittest_testcase_tagged",
        (addon_name, "__manifest__.py"),
        version,
        expected,
    )
