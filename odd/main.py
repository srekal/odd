import argparse
import collections
import logging
import pathlib
import typing

import lxml
import parso
import pkg_resources
from odd.addon import Addon, AddonPath, discover_addons, parse_manifest
from odd.checks import AddonCheck, PathCheck, PythonCheck, XMLCheck
from odd.const import SUPPORTED_VERSIONS
from odd.typedefs import OdooVersion
from odd.utils import format_issue, list_files
from odd.xmlutils import get_root

_LOG = logging.getLogger(__name__)

AddonType = typing.Type[typing.Union[AddonCheck, PathCheck, PythonCheck, XMLCheck]]


def get_checks(
    whitelist: typing.Optional[typing.Iterable[str]] = None
) -> typing.Dict[str, AddonType]:
    whitelist = set([] if whitelist is None else whitelist)
    use_whitelist = bool(whitelist)
    checks: typing.Dict[str, AddonType] = collections.OrderedDict()
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


def check_addon(
    manifest_path: pathlib.Path,
    checks: typing.Mapping[
        str, typing.Type[typing.Union[AddonCheck, PathCheck, PythonCheck, XMLCheck]]
    ],
    *,
    version: OdooVersion,
):
    addon_path = AddonPath(manifest_path)
    # FIXME: Make a function to do the separation.
    addon_checks, path_checks, python_checks, xml_checks = {}, {}, {}, {}

    for check_name, check_cls in checks.items():
        if issubclass(check_cls, AddonCheck):
            addon_checks[check_name] = check_cls()
        elif issubclass(check_cls, PathCheck):
            path_checks[check_name] = check_cls()
        elif issubclass(check_cls, PythonCheck):
            python_checks[check_name] = check_cls()
        elif issubclass(check_cls, XMLCheck):
            xml_checks[check_name] = check_cls()
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
    grammar = parso.load_grammar(version="2.7" if addon.version < 11 else "3.5")

    for addon_check in addon_checks.values():
        yield from addon_check.check(addon)

    for path in list_files(addon.path, list_dirs=True):
        for path_check in path_checks.values():
            yield from path_check.check(addon, path)

        if not path.is_file():
            continue

        if python_checks and path.suffix.lower() == ".py":
            with path.open(mode="rb") as f:
                module = grammar.parse(f.read())
            for python_check in python_checks.values():
                yield from python_check.check(addon, path, module)

        if xml_checks and path.suffix.lower() == ".xml":
            try:
                tree = get_root(path)
            except lxml.etree.XMLSyntaxError:
                _LOG.exception("Error while parsing XML file: %s", path)
            for xml_check in xml_checks.values():
                yield from xml_check.check(addon, path, tree)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", metavar="PATH", type=pathlib.Path, nargs="+")
    parser.add_argument("-w", "--whitelist", metavar="CHECK", nargs="*")
    parser.add_argument("version", type=int, choices=SUPPORTED_VERSIONS)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    checks = get_checks(whitelist=args.whitelist)
    num_issues = 0
    for path in args.paths:
        for manifest_path in discover_addons(path):
            for issue in check_addon(manifest_path, checks, version=args.version):
                num_issues += 1
                print(format_issue(issue))
    if not num_issues:
        _LOG.info("That's odd, no issues were found")
