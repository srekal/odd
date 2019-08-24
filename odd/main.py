import argparse
import collections
import logging
import pathlib
import typing

import pkg_resources
from odd.addon import Addon, ManifestPath, discover_addons, parse_manifest
from odd.check import Check
from odd.const import SUPPORTED_VERSIONS
from odd.issue import Issue
from odd.typedefs import OdooVersion
from odd.utils import format_issue
from odd.artifact import Artifact

_LOG = logging.getLogger(__name__)


def get_checks(
    whitelist: typing.Optional[typing.Iterable[str]] = None
) -> typing.Dict[str, typing.Type[Check]]:
    whitelist = set([] if whitelist is None else whitelist)
    use_whitelist = bool(whitelist)
    checks: typing.Dict[str, typing.Type[Check]] = collections.OrderedDict()
    for entry_point in pkg_resources.iter_entry_points("odd.check"):
        check_name = entry_point.name
        if whitelist and check_name not in whitelist:
            continue
        try:
            check_cls = entry_point.load()
        except Exception:  # pylint: disable=broad-except
            _LOG.exception('An error occured while loading check "%s".', check_name)
        else:
            checks[check_name] = check_cls
        finally:
            whitelist.discard(check_name)
            if use_whitelist and not whitelist:
                break

    for check_name in whitelist:
        raise KeyError(f'Check "{check_name}" not found.')

    return checks


def get_artifact_types() -> typing.Dict[str, typing.Type[Artifact]]:
    return {
        ep.name: ep.load()
        for ep in pkg_resources.iter_entry_points("odd.artifact_type")
    }


def check_addon(
    manifest_path: ManifestPath,
    checks: typing.Mapping[str, typing.Type[Check]],
    *,
    version: OdooVersion,
):
    artifact_types = get_artifact_types()
    artifact_type_inverse = {cls_: name for name, cls_ in artifact_types.items()}
    emitters: typing.Dict[str, typing.List[str]] = collections.defaultdict(list)
    handlers: typing.Dict[str, typing.List[str]] = collections.defaultdict(list)
    check_instances = {}

    for check_name, check_cls in checks.items():
        load = True
        for emit in check_cls._emits:
            if emit not in artifact_types:
                _LOG.error(
                    "Check: %s emits unknown artifact type: %s. "
                    "It will not be loaded.",
                    check_name,
                    emit,
                )
                load = False
                break
            else:
                emitters[emit].append(check_name)

        if not load:
            continue

        for handle in check_cls._handles:
            if handle not in artifact_types:
                _LOG.warning(
                    "Check: %s handles unknown artifact type: %s.", check_name, handle
                )
            else:
                handlers[handle].append(check_name)

        if load:
            check_instances[check_name] = check_cls()
        """
        for method_name, _ in inspect.getmembers(
            check_cls, predicate=inspect.isfunction
        ):
            if not method_name.startswith("on_"):
                continue
            checks_by_type[method_name][check_name] = check
        """

    # TODO: Validate check types.

    try:
        manifest = parse_manifest(manifest_path)
    except Exception as exc:
        raise SystemExit(
            f'Error while parsing the manifest of "{manifest_path.name}"'
            f"({manifest_path.path}): {exc}"
        )

    addon = Addon(manifest_path, manifest, version)
    artifacts = collections.deque([addon])

    def _handle_artifact(a, handler_name):
        if isinstance(a, Issue):
            yield a
        elif isinstance(a, Artifact):
            artifacts.append(a)
        else:
            _LOG.warning(
                "Unknown result type (%s) received from handler: %s",
                type(a),
                handler_name,
            )

    while artifacts:
        artifact = artifacts.popleft()
        artifact_type_name = artifact_type_inverse[type(artifact)]

        for handler_name in handlers[artifact_type_name]:
            handler = check_instances[handler_name]
            for new_artifact in getattr(handler, f"on_{artifact_type_name}")(artifact):
                yield from _handle_artifact(new_artifact, handler_name)

    for check in check_instances.values():
        if hasattr(check, "on_after"):
            yield from check.on_after(addon)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        dest="loglevel",
        action="store_const",
        const=logging.DEBUG,
        help="output debugging messages",
        default=logging.INFO,
    )
    parser.add_argument("paths", metavar="PATH", type=pathlib.Path, nargs="+")
    parser.add_argument("-w", "--whitelist", metavar="CHECK", nargs="*")
    parser.add_argument("version", type=int, choices=SUPPORTED_VERSIONS)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    checks = get_checks(whitelist=args.whitelist)
    num_issues = 0
    for path in args.paths:
        for manifest_path in discover_addons(path):
            for issue in check_addon(manifest_path, checks, version=args.version):
                num_issues += 1
                print(format_issue(issue))
    if not num_issues:
        _LOG.info("That's odd, no issues were found")
