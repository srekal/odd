import argparse
import collections
import pathlib
import typing

import pkg_resources
from odin.addon import Addon, AddonPath, discover_addons, parse_manifest
from odin.checks import AddonCheck, FileCheck
from odin.const import SUPPORTED_VERSIONS
from odin.typedefs import OdooVersion
from odin.utils import format_issue, get_addon_files


def get_checks(
    whitelist: typing.Optional[typing.Iterable[str]] = None
) -> typing.Dict[str, typing.Union[AddonCheck, FileCheck]]:
    whitelist = set([] if whitelist is None else whitelist)
    use_whitelist = bool(whitelist)
    checks = collections.OrderedDict()
    for entry_point in pkg_resources.iter_entry_points("odin.check"):
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


def check_addon(
    manifest_path: pathlib.Path,
    checks: typing.Mapping[str, typing.Type[typing.Union[AddonCheck, FileCheck]]],
    *,
    version: typing.Optional[OdooVersion] = None,
):
    addon_path = AddonPath(manifest_path)
    addon_checks, file_checks = {}, {}

    for check_name, check_cls in checks.items():
        if issubclass(check_cls, AddonCheck):
            addon_checks[check_name] = check_cls()
        elif issubclass(check_cls, FileCheck):
            file_checks[check_name] = check_cls()
        else:
            raise TypeError(f"Unsupported check class: {check_cls}")

    try:
        manifest = parse_manifest(addon_path)
    except Exception as exc:
        raise SystemExit(
            f'Error while parsing the manifest of "{addon_path.name}"'
            f"({addon_path.manifest_path}): {exc}"
        )

    addon = Addon(manifest_path, manifest, version)

    for addon_check in addon_checks.values():
        yield from addon_check.check(addon)

    for file_path in get_addon_files(addon.addon_path):
        for file_check in file_checks.values():
            yield from file_check.check(file_path, addon)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", type=pathlib.Path, nargs="+")
    parser.add_argument("-w", "--whitelist", metavar="CHECKS", nargs="*")
    parser.add_argument("version", type=int, choices=SUPPORTED_VERSIONS)
    args = parser.parse_args()

    checks = get_checks(whitelist=args.whitelist)
    for path in args.paths:
        for manifest_path in discover_addons(path):
            for issue in check_addon(manifest_path, checks, version=args.version):
                print(format_issue(issue))
