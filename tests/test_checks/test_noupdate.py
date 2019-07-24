import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon
from odin.checks.xml import NoUpdate


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "noupdate_cron",
            12,
            [
                {
                    "slug": "expected_noupdate_flag",
                    "description": '`ir.cron` model records should be declared in a `noupdate="1"` XML data section to allow user modifications',
                    "categories": ["correctness"],
                    "locations": [(["data", "ir_cron.xml"], [5, 3])],
                }
            ],
        ),
        ("noupdate_cron_extension", 12, []),
        ("noupdate_cron_odoo_1", 12, []),
        (
            "noupdate_cron_odoo_0",
            12,
            [
                {
                    "slug": "expected_noupdate_flag",
                    "description": '`ir.cron` model records should be declared in a `noupdate="1"` XML data section to allow user modifications',
                    "categories": ["correctness"],
                    "locations": [(["data", "ir_cron.xml"], [5, 3])],
                }
            ],
        ),
    ],
)
def test_noupdate(test_data_dir, addon_name, version, expected):
    manifest_path = test_data_dir / "noupdate" / addon_name / "__manifest__.py"
    addon_path = AddonPath(manifest_path)
    issues = list(check_addon(manifest_path, {"noupdate": NoUpdate}, version=version))

    expected_issues = []
    for issue in expected:
        locations = []
        for path_parts, line_nos in issue.pop("locations", []):
            locations.append(
                Location(manifest_path.parent.joinpath(*path_parts), line_nos)
            )

        expected_issues.append(
            Issue(**{"addon_path": addon_path, "locations": locations, **issue})
        )

    assert issues == expected_issues
