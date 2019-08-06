import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        ("qweb", []),
        (
            "xml_not_included",
            [
                {
                    "slug": "data_file_missing_in_manifest",
                    "description": (
                        "Data file is not included in `demo` or `data` "
                        "sections in the manifest file"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["views", "foo.xml"], [])],
                }
            ],
        ),
    ],
)
def test_data_file_inclusion(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir,
        "data_file_inclusion",
        (addon_name, "__manifest__.py"),
        12,
        expected,
    )
