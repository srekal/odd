import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "no_group",
            [
                {
                    "slug": "ir_model_access_without_group",
                    "description": (
                        "`ir.model.access` record (access_foo_no_group) "
                        "allows the following operations to users without group: "
                        "read, unlink"
                    ),
                    "categories": ["security", "correctness"],
                    "locations": [(["security", "ir.model.access.csv"], [3])],
                }
            ],
        )
    ],
)
def test_ir_model_access_no_group(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir,
        "ir_model_access_no_group",
        (addon_name, "__manifest__.py"),
        12,
        expected,
    )
