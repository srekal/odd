import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "file_permissions",
            [
                {
                    "slug": "file_permissions",
                    "description": "Files should have 644 permissions (current: 664)",
                    "locations": [(["__manifest__.py"], [])],
                    "categories": ["correctness"],
                }
            ],
        )
    ],
)
def test_file_permissions(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir, "file_permissions", ("__manifest__.py",), 12, expected
    )
