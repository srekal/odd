import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "duplicated_field",
            [
                {
                    "slug": "duplicate_record_field",
                    "description": (
                        '`foo` record "foo_1" has duplicated values for field "a"'
                    ),
                    "locations": [
                        (["data", "foo.xml"], [5]),
                        (["data", "foo.xml"], [7]),
                    ],
                    "categories": ["correctness", "maintainability"],
                }
            ],
        ),
        (
            "duplicated_field_no_id",
            [
                {
                    "slug": "duplicate_record_field",
                    "description": ('`foo` record has duplicated values for field "a"'),
                    "locations": [
                        (["data", "foo.xml"], [5]),
                        (["data", "foo.xml"], [7]),
                    ],
                    "categories": ["correctness", "maintainability"],
                }
            ],
        ),
    ],
)
def test_duplicate_record_fields(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir,
        "duplicate_record_fields",
        (addon_name, "__manifest__.py"),
        12,
        expected,
    )
