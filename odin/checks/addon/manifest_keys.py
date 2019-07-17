from odin.checks import AddonCheck
from odin.issue import Issue, Location


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
    # OCA.
    "maintainers",
    "development_status",
}


class ManifestKeys(AddonCheck):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._checked_addons = set()

    def _check_active(self, manifest):
        if "active" in manifest:
            yield {
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
                yield {
                    "slug": "deprecated_manifest_key",
                    "description": f'"{key}" manifest key was deprecated in favor of "{correct_key}"',
                    "categories": ["correctness", "deprecated"],
                }

    def _check_unknown_keys(self, manifest):
        unknown_keys = manifest.keys() - KNOWN_KEYS
        for key in unknown_keys:
            yield {
                "slug": "unknown_manifest_key",
                "description": f'Unknown manifest key "{key}"',
                "categories": ["correctness"],
            }

    def check(self, addon):
        if addon.name in self._checked_addons:
            return
        for check in ("active", "deprecated_xml", "unknown_keys"):
            for issue in getattr(self, f"_check_{check}")(addon.manifest):
                yield Issue(
                    **{
                        "locations": [Location(addon.manifest_path)],
                        "addon_path": addon.addon_path,
                        **issue,
                    }
                )
        self._checked_addons.add(addon.name)
