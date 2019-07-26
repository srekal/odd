import functools
import operator
import pathlib
import typing

import yarl
from odin.addon import AddonPath
from odin.const import SUPPORTED_VERSIONS
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


def list_files(
    dir: pathlib.Path,
    *,
    list_dirs: bool = False,
    exclude_dirs: typing.Optional[typing.Iterable[pathlib.Path]] = None,
):
    exclude_dirs = set(exclude_dirs) if exclude_dirs else set()
    for path in dir.iterdir():
        if path.is_dir():
            if path in exclude_dirs:
                continue
            if list_dirs:
                yield path
            yield from list_files(path, list_dirs=list_dirs, exclude_dirs=exclude_dirs)
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


def _get_operator(version_spec: str, version_cls):
    for prefix, op in (
        ("*", lambda a, b: bool(a)),
        ("<=", operator.le),
        ("<", operator.lt),
        (">=", operator.ge),
        (">", operator.gt),
        ("!=", operator.ne),
        ("!", operator.ne),
        ("==", operator.eq),
        ("=", operator.eq),
    ):
        if version_spec.startswith(prefix):
            return op, version_cls(version_spec[len(prefix) :])

    raise ValueError(f"Invalid version specification: {version_spec}")


def lookup_version_list(
    version_map: typing.Mapping[str, typing.List[typing.Any]],
    version: int,
    *,
    result_cls=list,
) -> typing.Union[typing.List[typing.Any], typing.Set[typing.Any]]:
    if not isinstance(version, int):
        raise TypeError(
            f"Invalid version, expected an integer, got {version} ({type(version)})"
        )
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(
            f'Unsupported version "{version}", must be one of {SUPPORTED_VERSIONS}'
        )

    result = result_cls()
    extend = result.extend if result_cls == list else result.update
    for version_ranges, values in version_map.items():
        for version_spec in version_ranges.split(","):
            op, v2 = _get_operator(version_spec, version_cls=int)
            if op(version, v2):
                extend(values)
    return result


def expand_version_list(
    version_map: typing.Mapping[str, typing.List[typing.Any]],
    *versions: int,
    result_cls=list,
) -> typing.Dict[int, typing.Union[typing.List[typing.Any], typing.Set[typing.Any]]]:
    result = {}
    for version in versions:
        result[version] = lookup_version_list(
            version_map, version, result_cls=result_cls
        )
    return result
