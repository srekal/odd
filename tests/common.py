import pathlib

import yarl

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon, get_checks


def run_check_test(data_dir, check_name, manifest_path_parts, version, issues):
    manifest_path = data_dir.joinpath(check_name, *manifest_path_parts)
    addon_path = AddonPath(manifest_path)
    expected_issues = []
    for issue in issues:
        locations = []
        for path_parts, line_nos in issue.pop("locations", []):
            locations.append(
                Location(manifest_path.parent.joinpath(*path_parts), line_nos)
            )

        sources = []
        for source in issue.pop("sources", []):
            sources.append(yarl.URL(source))

        expected_issues.append(
            Issue(
                **{
                    "addon_path": addon_path,
                    "locations": locations,
                    "sources": sources,
                    **issue,
                }
            )
        )

    actual_issues = list(
        check_addon(manifest_path, get_checks({check_name}), version=version)
    )

    assert expected_issues == actual_issues
