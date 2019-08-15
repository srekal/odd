import argparse
import collections
import inspect
import logging
import pathlib
import typing

import lxml
import parso
import pkg_resources
from odd.addon import Addon, AddonPath, discover_addons, parse_manifest
from odd.check import Check
from odd.const import SUPPORTED_VERSIONS
from odd.typedefs import OdooVersion
from odd.utils import format_issue, list_files
from odd.xmlutils import get_root

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


def check_addon(
    manifest_path: pathlib.Path,
    checks: typing.Mapping[str, typing.Type[Check]],
    *,
    version: OdooVersion,
):
    addon_path = AddonPath(manifest_path)
    # FIXME: Make a function to do the separation.
    checks_by_type: typing.DefaultDict[
        str, typing.Dict[str, Check]
    ] = collections.defaultdict(dict)

    for check_name, check_cls in checks.items():
        check = check_cls()
        for method_name, _ in inspect.getmembers(
            check_cls, predicate=inspect.isfunction
        ):
            if not method_name.startswith("on_"):
                continue
            checks_by_type[method_name][check_name] = check

    # TODO: Validate check types.

    try:
        manifest = parse_manifest(addon_path)
    except Exception as exc:
        raise SystemExit(
            f'Error while parsing the manifest of "{addon_path.name}"'
            f"({addon_path.manifest_path}): {exc}"
        )

    addon = Addon(manifest_path, manifest, version)
    grammar = parso.load_grammar(version="2.7" if addon.version < 11 else "3.5")

    for before_check in checks_by_type["on_before"].values():
        yield from getattr(before_check, "on_before")(addon)

    for path in list_files(addon.path, list_dirs=True):
        for path_check in checks_by_type["on_path"].values():
            yield from getattr(path_check, "on_path")(addon, path)

        if not path.is_file():
            continue

        if checks_by_type["on_python_module"] and path.suffix.lower() == ".py":
            with path.open(mode="rb") as f:
                module = grammar.parse(f.read())
            for python_check in checks_by_type["on_python_module"].values():
                yield from getattr(python_check, "on_python_module")(
                    addon, path, module
                )

        if checks_by_type["on_xml_tree"] and path.suffix.lower() == ".xml":
            try:
                tree = get_root(path)
            except lxml.etree.XMLSyntaxError:
                _LOG.exception("Error while parsing XML file: %s", path)
            else:
                for xml_check in checks_by_type["on_xml_tree"].values():
                    yield from getattr(xml_check, "on_xml_tree")(addon, path, tree)

    for after_check in checks_by_type["on_after"].values():
        yield from getattr(after_check, "on_after")(addon)


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
