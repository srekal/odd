import functools
import pathlib
import typing

import yarl

from odin.addon import AddonPath
from odin.issue import Issue


def odoo_commit_url(commit: str) -> yarl.URL:
    return yarl.URL(f"https://github.com/odoo/odoo/commit/{commit}")


def odoo_source_url(
    commit: str,
    path: str,
    *,
    start: typing.Optional[int] = None,
    end: typing.Optional[int] = None,
) -> yarl.URL:
    if end and not start:
        raise ValueError("`start` must be provided if `end` is provided")

    fragment = None
    if start is not None:
        fragment = f"L{start:d}" if end is None else f"L{start:d}-L{end:d}"

    return yarl.URL.build(
        scheme="https",
        host="github.com",
        path=f"/odoo/odoo/blob/{commit}/{path}",
        fragment=fragment,
    )


def list_files(dir: pathlib.Path, list_dirs=False):
    for path in dir.iterdir():
        if path.is_dir():
            if list_dirs:
                yield path
            yield from list_files(path)
        else:
            yield path


@functools.lru_cache(maxsize=128)
def get_addon_files(addon_path: AddonPath):
    yield from list_files(addon_path.path)


def format_issue(issue: Issue) -> str:
    locations = []
    if issue.locations:
        for location in issue.locations:
            relative_path = location.path.relative_to(issue.addon_path.path)
            line_numbers = ""
            if location.line_numbers:
                if len(location.line_numbers) > 1:
                    line_numbers = ", lines: %s" % (
                        ", ".join(str(line_no) for line_no in location.line_numbers)
                    )
                else:
                    line_numbers = ", line: %s" % location.line_numbers[0]

            locations.append(f"{relative_path!s}{line_numbers}")

    location_str = " (%s)" % "; ".join(locations) if locations else ""

    return f"{issue.addon_path.name}{location_str}: {issue.description}"
