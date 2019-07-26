import ast
import logging
import sys

from odin.checks import FileCheck
from odin.const import SUPPORTED_VERSIONS
from odin.issue import Issue, Location
from odin.utils import expand_version_list, lookup_version_list

_logger = logging.getLogger(__name__)


ROUTE_KWARG_VERSION_MAP = {
    ">=8": ["auth", "methods", "multilang", "type", "website"],
    ">=9": ["cors", "csrf"],
    ">=11": ["sitemap"],
    ">=12": ["save_session"],
}

ROUTE_KWARGS = expand_version_list(
    ROUTE_KWARG_VERSION_MAP, *SUPPORTED_VERSIONS, result_cls=set
)


class RouteKwargs(FileCheck):
    def check(self, filename, addon):
        if filename.suffix.lower() != ".py":
            return

        with filename.open(mode="rt") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError as exc:
                _logger.warning(
                    "A syntax error occurred while parsing Python module: %s. "
                    "It either contains syntax errors or was written for a different "
                    "Python version (ours is %s).",
                    filename,
                    ".".join(map(str, sys.version_info[:3])),
                )
                return

            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue

                for dec_node in node.decorator_list:
                    if not isinstance(dec_node, ast.Call):
                        continue
                    elif not dec_node.keywords:
                        continue

                    if isinstance(dec_node.func, ast.Name):
                        dec_name = dec_node.func.id
                    else:
                        dec_name = dec_node.func.attr

                    if dec_name != "route":
                        continue

                    for kw in {kw.arg for kw in dec_node.keywords} - ROUTE_KWARGS[
                        addon.version
                    ]:
                        yield Issue(
                            "unknown_route_kwarg",
                            f'Controller method `{node.name}` has an unknown `route()` keyword argument "{kw}"',
                            addon.addon_path,
                            [Location(filename, [dec_node.lineno])],
                            categories=["correctness"],
                        )
