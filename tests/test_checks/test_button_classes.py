import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "button_classes",
            [
                {
                    "slug": "deprecated_button_class",
                    "description": (
                        "`oe_highlight` button class is deprecated since v12.0 "
                        "in favor of `btn-primary`"
                    ),
                    "categories": ["maintainability", "deprecated"],
                    "locations": [(["views", "foo.xml"], [11])],
                    "sources": [
                        "https://github.com/odoo/odoo/blob"
                        "/1e5fbb8e5bf0e0458d83a399b2b59d03a601e86a"
                        "/addons/web/static/src/js/core/dom.js#L340-L345"
                    ],
                },
                {
                    "slug": "deprecated_button_class",
                    "description": (
                        "`oe_link` button class is deprecated since v12.0 "
                        "in favor of `btn-link`"
                    ),
                    "locations": [(["views", "foo.xml"], [23])],
                    "categories": ["maintainability", "deprecated"],
                    "sources": [
                        "https://github.com/odoo/odoo/blob"
                        "/1e5fbb8e5bf0e0458d83a399b2b59d03a601e86a"
                        "/addons/web/static/src/js/core/dom.js#L340-L345"
                    ],
                },
            ],
        )
    ],
)
def test_button_classes(test_data_dir, addon_name, expected):
    run_check_test(test_data_dir, "button_classes", ("__manifest__.py",), 12, expected)
