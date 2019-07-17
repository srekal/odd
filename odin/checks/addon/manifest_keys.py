from odin.checks import AddonCheck
from odin.issue import Issue, Location


KNOWN_KEYS = {
    'name',
    'version',
    'description',
    'author',
    'website',
    'license',
    'category',
    'depends',
    'data',
    'demo',
    'auto_install',
    'external_dependencies',
    'application',
    'css',
    'images',
    'installable',
    'maintainer',
    'summary',
    'qweb',
    'sequence',
    'bootstrap',
    'pre_init_hook',
    'post_init_hook',
    'uninstall_hook',
}


class ManifestKeys(AddonCheck):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._checked_addons = set()

    def check(self, addon):
        if addon.name in self._checked_addons:
            return
        unknown_keys = addon.manifest.keys() - KNOWN_KEYS
        for key in unknown_keys:
            yield Issue(
                'unknown_manifest_key',
                f'Unknown manifest key "{key}"',
                addon.addon_path,
                [
                    Location(addon.manifest_path),
                ],
                categories=["correctness"],
            )

        self._checked_addons.add(addon.name)