import pathlib

import yarl

from odd.addon import ManifestPath
from odd.issue import Issue, Location
from odd.main import check_addon, get_checks


def run_check_test(
    data_dir: pathlib.Path,
    check_name,
    manifest_path_parts,
    version,
    issues,
    extra_checks=(
        "addon_path_emitter",
        "addon_file_emitter",
        "xml_tree_emitter",
        "python_emitter",
        "external_id_emitter",
    ),
):
    manifest_path = ManifestPath(data_dir.joinpath(check_name, *manifest_path_parts))
    expected_issues = []
    for issue in issues:
        locations = []
        for path_parts, line_nos in issue.pop("locations", []):
            locations.append(
                Location(manifest_path.addon_path.joinpath(*path_parts), line_nos)
            )

        sources = []
        for source in issue.pop("sources", []):
            sources.append(yarl.URL(source))

        expected_issues.append(
            Issue(
                **{
                    "manifest_path": manifest_path,
                    "locations": locations,
                    "sources": sources,
                    **issue,
                }
            )
        )

    checks_to_load = {check_name}
    if extra_checks:
        checks_to_load.update(extra_checks)

    actual_issues = list(
        check_addon(manifest_path, get_checks(checks_to_load), version=version)
    )

    assert expected_issues == actual_issues
