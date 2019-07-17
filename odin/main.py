import argparse
import ast
import pathlib
import typing

from odin.addon import Addon, AddonPath
from odin.checks.addon import DirectoryPermissions, FilePermissions, ManifestKeys
from odin.checks.xml import SearchString, TreeString
from odin.const import SUPPORTED_VERSIONS
from odin.typedefs import OdooVersion
from odin.utils import get_addon_files, format_issue

from . import const


def parse_manifest(addon_path: AddonPath):
    with addon_path.manifest_path.open(mode="r") as f:
        return ast.literal_eval(f.read())


def find_manifest(path: pathlib.Path):
    for child in path.iterdir():
        if (
            child.is_file()
            and child.name in const.MANIFEST_FILENAMES
        ):
            return child


def discover_addons(dir_path: pathlib.Path) -> typing.Generator[pathlib.Path, None, None]:
    for child in dir_path.iterdir():
        if child.is_dir():
            manifest = find_manifest(child)
            if manifest:
                yield manifest
            else:
                yield from discover_addons(child)


def get_xml_checks():
    return {"search_string": SearchString(), "tree_string": TreeString()}


def get_addon_checks():
    return {
        "directory_permissions": DirectoryPermissions(),
        "file_permissions": FilePermissions(),
        "manifest_keys": ManifestKeys(),
    }


def check_addon(manifest_path: pathlib.Path, version: typing.Optional[OdooVersion] = None):
    addon_path = AddonPath(manifest_path)

    try:
        manifest = parse_manifest(addon_path)
    except Exception as exc:
        raise SystemExit(
            f'Error while parsing the manifest of "{addon_path.name}"'
            f"({addon_path.manifest_path}): {exc}"
        )

    addon = Addon(manifest_path, manifest, version)

    for check_name, func in get_addon_checks().items():
        yield from func.check(addon)

    for file_path in get_addon_files(addon.addon_path):
        for check_name, func in get_xml_checks().items():
            yield from func.check(file_path, addon)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("version", type=int, choices=SUPPORTED_VERSIONS)
    args = parser.parse_args()

    for manifest_path in discover_addons(args.path):
        for issue in check_addon(manifest_path, version=args.version):
            print(format_issue(issue))
