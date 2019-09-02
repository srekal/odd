import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "record_wo_id",
            [
                {
                    "slug": "xml_operation_without_id",
                    "description": ("XML operation `<record>` has no `id` attribute"),
                    "locations": [(["data", "foo.xml"], [4])],
                    "categories": ["maintainability"],
                }
            ],
        ),
        ("record_w_id", []),
    ],
)
def test_xml_operation_no_id(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir,
        "xml_operation_no_id",
        (addon_name, "__manifest__.py"),
        12,
        expected,
    )
