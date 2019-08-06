import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "manifest_keys_unknown_keys",
            [
                {
                    "slug": "unknown_manifest_key",
                    "description": 'Unknown manifest key "foo"',
                    "categories": ["correctness"],
                    "locations": [(["__manifest__.py"], [(1, 47)])],
                }
            ],
        ),
        (
            "manifest_keys_unknown_keys_complex",
            [
                {
                    "slug": "unknown_manifest_key",
                    "description": 'Unknown manifest key "foo"',
                    "categories": ["correctness"],
                    "locations": [(["__manifest__.py"], [(13, 5)])],
                }
            ],
        ),
        (
            "manifest_keys_active",
            [
                {
                    "slug": "deprecated_manifest_key",
                    "description": (
                        '"active" manifest key was renamed to "auto_install"'
                    ),
                    "categories": ["correctness", "deprecated"],
                    "locations": [(["__manifest__.py"], [(1, 41)])],
                }
            ],
        ),
        (
            "manifest_keys_deprecated_xml",
            [
                {
                    "slug": "deprecated_manifest_key",
                    "description": (
                        '"demo_xml" manifest key was deprecated in favor of "demo"'
                    ),
                    "categories": ["correctness", "deprecated"],
                    "locations": [(["__manifest__.py"], [(1, 49)])],
                }
            ],
        ),
        (
            "manifest_keys_deprecated_xml_init_xml",
            [
                {
                    "slug": "deprecated_manifest_key",
                    "description": (
                        '"init_xml" manifest key was deprecated in favor of "data"'
                    ),
                    "categories": ["correctness", "deprecated"],
                    "locations": [(["__manifest__.py"], [(1, 58)])],
                }
            ],
        ),
        ("manifest_keys_deprecated_xml_init_xml_csv", []),
    ],
)
def test_file_permissions(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir, "manifest_keys", (addon_name, "__manifest__.py"), 12, expected
    )
