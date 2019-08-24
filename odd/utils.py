import operator
import pathlib
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple, Union

import yarl
from odd.const import SUPPORTED_VERSIONS
from odd.issue import Issue


def odoo_commit_url(commit: str) -> yarl.URL:
    return yarl.URL(f"https://github.com/odoo/odoo/commit/{commit}")


def odoo_source_url(
    commit: str, path: str, *, start: Optional[int] = None, end: Optional[int] = None
) -> yarl.URL:
    if end and not start:
        raise ValueError("`start` must be provided if `end` is provided")

    fragment = ""
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
    exclude_dirs: Optional[Iterable[pathlib.Path]] = None,
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


def _fmt_line_no(line_no: Union[int, Tuple[int, int]]) -> str:
    if isinstance(line_no, tuple):
        return "%d, column: %d" % (line_no[0], line_no[1])
    else:
        return "%d" % line_no


def format_issue(issue: Issue) -> str:
    locations = []
    if issue.locations:
        for location in issue.locations:
            relative_path = location.path.relative_to(issue.manifest_path.addon_path)
            line_numbers = ""
            if location.line_numbers:
                if len(location.line_numbers) > 1:
                    line_numbers = ", lines: %s" % (
                        ", ".join(
                            _fmt_line_no(line_no) for line_no in location.line_numbers
                        )
                    )
                else:
                    line_numbers = ", line: %s" % _fmt_line_no(location.line_numbers[0])

            locations.append(f"{relative_path!s}{line_numbers}")

    location_str = " (%s)" % "; ".join(locations) if locations else ""

    return f"{issue.manifest_path.name}{location_str}: {issue.description}"


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
    version_map: Mapping[str, Union[List[Any], Set[Any], Dict[Any, Any]]],
    version: int,
    *,
    result_cls=list,
) -> Union[List[Any], Set[Any], Dict[Any, Any]]:
    if not isinstance(version, int):
        raise TypeError(
            f"Invalid version, expected an integer, got {version} ({type(version)})"
        )
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(
            f'Unsupported version "{version}", must be one of {SUPPORTED_VERSIONS}'
        )

    result = result_cls()
    if result_cls == list:
        extend = result.extend
    elif result_cls == set or result_cls == dict:
        extend = result.update
    else:
        raise TypeError(f"Unknown type for `result_cls`: {type(result_cls)}")
    for version_ranges, values in version_map.items():
        for version_spec in version_ranges.split(","):
            op, v2 = _get_operator(version_spec, version_cls=int)
            if op(version, v2):
                extend(values)
    return result


def expand_version_list(
    version_map: Mapping[str, Union[List[Any], Set[Any], Dict[Any, Any]]],
    *versions: int,
    result_cls=list,
) -> Dict[int, Union[List[Any], Set[Any], Dict[Any, Any]]]:
    result = {}
    for version in versions:
        result[version] = lookup_version_list(
            version_map, version, result_cls=result_cls
        )
    return result


def split_external_id(external_id: str) -> Tuple[Optional[str], str]:
    if not external_id:
        raise ValueError(
            f'Expected non-empty string, got: "{external_id}"'
            f" (type: {type(external_id)})"
        )
    addon_name, record_id = None, external_id
    if "." in external_id:
        addon_name, record_id = external_id.split(".")[:2]
    return addon_name, record_id
