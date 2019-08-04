from odin.checks import PythonCheck
from odin.const import SUPPORTED_VERSIONS
from odin.issue import Issue, Location
from odin.utils import expand_version_list
from odin.parso_utils import extract_func_name, walk

ROUTE_KWARG_VERSION_MAP = {
    ">=8": ["auth", "methods", "multilang", "type", "website"],
    ">=9": ["cors", "csrf"],
    ">=11": ["sitemap"],
    ">=12": ["save_session"],
}

ROUTE_KWARGS = expand_version_list(
    ROUTE_KWARG_VERSION_MAP, *SUPPORTED_VERSIONS, result_cls=set
)


class RouteKwargs(PythonCheck):
    def check(self, addon, filename, module):
        for node in walk(module):
            if node.type != "decorator":
                continue

            name_parts = extract_func_name(node)
            if (len(name_parts) == 1 and name_parts[0] != "route") or (
                len(name_parts) == 2
                and (name_parts[0] != "http" or name_parts[1] != "route")
            ):
                continue

            kwargs = {
                c.children[0].value: (c.children[0].line, c.children[0].start_pos)
                for c in walk(node)
                if c.type == "argument"
            }

            for kw in kwargs.keys() - ROUTE_KWARGS[addon.version]:
                yield Issue(
                    "unknown_route_kwarg",
                    f'Unknown `http.route()` keyword argument "{kw}"',
                    addon.addon_path,
                    [Location(filename, [kwargs[kw][0]])],
                    categories=["correctness"],
                )