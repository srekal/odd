import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


@pytest.mark.parametrize(
    "addon_name, expected_issues",
    [
        (
            "manifest_keys_unknown_keys",
            [
                {
                    "slug": "unknown_manifest_key",
                    "description": 'Unknown manifest key "foo"',
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "manifest_keys_active",
            [
                {
                    "slug": "deprecated_manifest_key",
                    "description": '"active" manifest key was renamed to "auto_install"',
                    "categories": ["correctness", "deprecated"],
                }
            ],
        ),
        (
            "manifest_keys_deprecated_xml",
            [
                {
                    "slug": "deprecated_manifest_key",
                    "description": '"demo_xml" manifest key was deprecated in favor of "demo"',
                    "categories": ["correctness", "deprecated"],
                }
            ],
        ),
        (
            "manifest_keys_deprecated_xml_init_xml",
            [
                {
                    "slug": "deprecated_manifest_key",
                    "description": '"init_xml" manifest key was deprecated in favor of "data"',
                    "categories": ["correctness", "deprecated"],
                }
            ],
        ),
        ("manifest_keys_deprecated_xml_init_xml_csv", []),
    ],
)
def test_file_permissions(addon_name, expected_issues, test_data_dir):
    manifest_path = test_data_dir / addon_name / "__manifest__.py"
    issues = list(check_addon(manifest_path, version=12))
    assert issues == [
        Issue(
            **{
                "addon_path": AddonPath(manifest_path),
                "locations": [Location(manifest_path)],
                **issue,
            }
        )
        for issue in expected_issues
    ]
