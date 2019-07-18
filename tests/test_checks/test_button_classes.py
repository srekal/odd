import pytest
import yarl
from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.main import check_addon


def test_button_classes(test_data_dir):
    manifest_path = test_data_dir / "button_classes" / "__manifest__.py"
    addon_path = AddonPath(manifest_path)
    issues = list(check_addon(manifest_path, version=12))
    assert issues == [
        Issue(
            "deprecated_button_class",
            "`oe_highlight` button class is deprecated since v12.0 in favor of `btn-primary`",
            addon_path,
            [Location(addon_path.path / "views/foo.xml", [11])],
            categories=["maintainability", "deprecated"],
            sources=[
                yarl.URL(
                    "https://github.com/odoo/odoo/blob/1e5fbb8e5bf0e0458d83a399b2b59d03a601e86a/addons/web/static/src/js/core/dom.js#L340-L345"
                )
            ],
        ),
        Issue(
            "deprecated_button_class",
            "`oe_link` button class is deprecated since v12.0 in favor of `btn-link`",
            addon_path,
            [Location(addon_path.path / "views/foo.xml", [23])],
            categories=["maintainability", "deprecated"],
            sources=[
                yarl.URL(
                    "https://github.com/odoo/odoo/blob/1e5fbb8e5bf0e0458d83a399b2b59d03a601e86a/addons/web/static/src/js/core/dom.js#L340-L345"
                )
            ],
        ),
    ]
