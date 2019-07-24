import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon
from odin.checks.addon import DataFileInclusion


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        ("qweb", []),
        (
            "xml_not_included",
            [
                {
                    "slug": "data_file_missing_in_manifest",
                    "description": "Data file is not included in `demo` or `data` sections in the manifest file",
                    "categories": ["correctness"],
                    "locations": [(["views", "foo.xml"])],
                }
            ],
        ),
    ],
)
def test_data_file_inclusion(test_data_dir, addon_name, expected):
    manifest_path = (
        test_data_dir / "data_file_inclusion" / addon_name / "__manifest__.py"
    )
    addon_path = AddonPath(manifest_path)
    issues = list(
        check_addon(
            manifest_path, {"data_file_inclusion": DataFileInclusion}, version=12
        )
    )

    expected_issues = []
    for issue in expected:
        locations = []
        for path_parts in issue.pop("locations", []):
            locations.append(Location(manifest_path.parent.joinpath(*path_parts)))

        expected_issues.append(
            Issue(**{"addon_path": addon_path, "locations": locations, **issue})
        )

    assert issues == expected_issues
