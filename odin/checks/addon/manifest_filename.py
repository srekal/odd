from odin.checks import AddonCheck
from odin.issue import Issue, Location
from odin.utils import odoo_commit_url


class ManifestFilename(AddonCheck):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._checked_addons = set()

    def check(self, addon):
        if addon.version < 10 or addon.name in self._checked_addons:
            return
        if addon.manifest_path.name != "__manifest__.py":
            yield Issue(
                "deprecated_manifest_filename",
                'Starting with Odoo 10, addon manifest files should be named "__manifest__.py"',
                addon.addon_path,
                [Location(addon.manifest_path)],
                categories=["deprecated"],
                sources=[odoo_commit_url("4339196e5231aa734a0154e2f4e88b2e54f27d48")],
            )
        self._checked_addons.add(addon.name)
