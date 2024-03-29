import collections

from odd.check import Check
from odd.const import MANIFEST_FILENAMES
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1, get_string_node_value, is_string_node, walk

KNOWN_KEYS = {
    "name",
    "version",
    "description",
    "author",
    "website",
    "license",
    "category",
    "depends",
    "data",
    "demo",
    "auto_install",
    "external_dependencies",
    "application",
    "css",
    "images",
    "installable",
    "maintainer",
    "summary",
    "qweb",
    "sequence",
    "bootstrap",
    "icon",
    # Hooks.
    "pre_init_hook",
    "post_init_hook",
    "uninstall_hook",
    "post_load",
    # Not sure about the purpose of this.
    "web",
    # TODO: Check if this makes sense in >= v12.
    "test",
    # Deprecated.
    "active",
    "init_xml",
    "update_xml",
    "demo_xml",
    # App store.
    "support",
    "price",
    "currency",
    "iap",
    "live_test_url",
    # OCA.
    "maintainers",
    "development_status",
}


class ManifestKeys(Check):
    _handles = {"python_module"}

    def _check_active(self, manifest):
        if "active" in manifest:
            yield "active", {
                "slug": "deprecated_manifest_key",
                "description": '"active" manifest key was renamed to "auto_install"',
                "categories": ["correctness", "deprecated"],
            }

    def _check_deprecated_xml(self, manifest):
        for key in ("init_xml", "update_xml", "demo_xml"):
            if key in manifest:
                if key == "init_xml":
                    files = manifest.get(key) or []
                    if not any(fn.endswith(".xml") for fn in files):
                        continue
                correct_key = "demo" if key == "demo_xml" else "data"
                yield key, {
                    "slug": "deprecated_manifest_key",
                    "description": (
                        f'"{key}" manifest key was deprecated '
                        f'in favor of "{correct_key}"'
                    ),
                    "categories": ["correctness", "deprecated"],
                }

    def _check_unknown_keys(self, manifest):
        unknown_keys = manifest.keys() - KNOWN_KEYS
        for key in unknown_keys:
            yield key, {
                "slug": "unknown_manifest_key",
                "description": f'Unknown manifest key "{key}"',
                "categories": ["correctness"],
            }

    def _get_key_locations(self, module):
        key_locations = collections.defaultdict(list)
        for node in walk(module):
            if node.type == "dictorsetmaker":
                for child in node.children[::4]:
                    if is_string_node(child):
                        key_locations[get_string_node_value(child)].append(
                            column_index_1(child.start_pos)
                        )
                break
        return key_locations

    def on_python_module(self, python_module):
        if python_module.path.name not in MANIFEST_FILENAMES:
            return
        key_locations = None
        for check in ("active", "deprecated_xml", "unknown_keys"):
            for key, issue in getattr(self, f"_check_{check}")(
                python_module.addon.manifest
            ):
                if key_locations is None:
                    key_locations = self._get_key_locations(python_module.module)
                yield Issue(
                    **{
                        "locations": [Location(python_module.path, key_locations[key])],
                        "manifest_path": python_module.addon.manifest_path,
                        **issue,
                    }
                )
