from odd.check import Check
from odd.const import SUPPORTED_VERSIONS
from odd.issue import Issue, Location
from odd.utils import expand_version_list
from odd.parso_utils import column_index_1, extract_func_name, walk

ROUTE_KWARG_VERSION_MAP = {
    ">=8": ["auth", "methods", "multilang", "type", "website"],
    ">=9": ["cors", "csrf"],
    ">=11": ["sitemap"],
    ">=12": ["save_session"],
}

ROUTE_KWARGS = expand_version_list(
    ROUTE_KWARG_VERSION_MAP, *SUPPORTED_VERSIONS, result_cls=set
)


class RouteKwargs(Check):
    _handles = {"python_module"}

    def on_python_module(self, python_module):
        for node in walk(python_module.module):
            if node.type != "decorator":
                continue

            name_parts = extract_func_name(node)
            if (len(name_parts) == 1 and name_parts[0] != "route") or (
                len(name_parts) == 2
                and (name_parts[0] != "http" or name_parts[1] != "route")
            ):
                continue

            kwargs = {
                c.children[0].value: (
                    c.children[0].line,
                    column_index_1(c.children[0].start_pos),
                )
                for c in walk(node)
                if c.type == "argument"
            }

            for kw in kwargs.keys() - ROUTE_KWARGS[python_module.addon.version]:
                yield Issue(
                    "unknown_route_kwarg",
                    f'Unknown `http.route()` keyword argument "{kw}"',
                    python_module.addon.manifest_path,
                    [Location(python_module.path, [kwargs[kw][0]])],
                    categories=["correctness"],
                )
