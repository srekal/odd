import argparse
import ast
import pathlib
import typing

from odin.addon import Addon, AddonPath
from odin.checks import AddonCheck, FileCheck
from odin.checks.addon import (
    ButtonClasses,
    DirectoryPermissions,
    FilePermissions,
    ManifestFilename,
    ManifestKeys,
)
from odin.checks.xml import SearchString, TreeString
from odin.const import SUPPORTED_VERSIONS
from odin.typedefs import OdooVersion
from odin.utils import format_issue, get_addon_files

from . import const


def find_manifest(path: pathlib.Path):
    for child in path.iterdir():
        if child.is_file() and child.name in const.MANIFEST_FILENAMES:
            return child


def discover_addons(
    dir_path: pathlib.Path
) -> typing.Generator[pathlib.Path, None, None]:
    for child in dir_path.iterdir():
        if child.is_dir():
            manifest = find_manifest(child)
            if manifest:
                yield manifest
            else:
                yield from discover_addons(child)


def get_checks():
    return {
        "search_string": SearchString,
        "tree_string": TreeString,
        "button_classes": ButtonClasses,
        "directory_permissions": DirectoryPermissions,
        "file_permissions": FilePermissions,
        "manifest_keys": ManifestKeys,
        "manifest_filename": ManifestFilename,
    }


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

    for func in addon_checks.values():
        yield from func.check(addon)

    for file_path in get_addon_files(addon.addon_path):
        for func in file_checks.values():
            yield from func.check(file_path, addon)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", type=pathlib.Path, nargs="+")
    parser.add_argument("version", type=int, choices=SUPPORTED_VERSIONS)
    args = parser.parse_args()

    checks = get_checks()
    for path in args.paths:
        for manifest_path in discover_addons(path):
            for issue in check_addon(manifest_path, checks, version=args.version):
                print(format_issue(issue))
