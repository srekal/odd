import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "directory_permissions",
            [
                {
                    "slug": "directory_permissions",
                    "description": (
                        "Directories should have 755 permissions (current: 775)"
                    ),
                    "locations": [(["views"], [])],
                    "categories": ["correctness"],
                }
            ],
        )
    ],
)
def test_directory_permissions(test_data_dir, addon_name, expected):
    (test_data_dir / "directory_permissions" / "views").chmod(0o775)
    run_check_test(
        test_data_dir, "directory_permissions", ("__manifest__.py",), 12, expected
    )
