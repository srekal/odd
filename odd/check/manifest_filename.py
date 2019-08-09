from odd.check import Check
from odd.issue import Issue, Location
from odd.utils import odoo_commit_url


class ManifestFilename(Check):
    def on_addon(self, addon):
        if addon.version >= 10 and addon.manifest_path.name != "__manifest__.py":
            yield Issue(
                "deprecated_manifest_filename",
                "Starting with Odoo 10, addon manifest files should be named "
                '"__manifest__.py"',
                addon.addon_path,
                [Location(addon.manifest_path)],
                categories=["deprecated"],
                sources=[odoo_commit_url("4339196e5231aa734a0154e2f4e88b2e54f27d48")],
            )
