import pytest
from odin.checks.addon import TrackVisibilityAlways

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "track_visibility_always",
            12,
            [
                {
                    "slug": "track_visibility_always_deprecated",
                    "description": 'Field `track_visibility` attribute value "always" is deprecated since version 12.0',
                    "categories": ["deprecated"],
                    "locations": [(["models", "foo.py"], [(10, 8)])],
                    "sources": [
                        "https://github.com/odoo/odoo/commit/c99de4551583e801ecc6669ac456c4f7e2eef1da"
                    ],
                }
            ],
        ),
        ("track_visibility_always", 11, []),
    ],
)
def test_track_visibility_always(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "track_visibility_always",
        (addon_name, "__manifest__.py"),
        version,
        TrackVisibilityAlways,
        expected,
    )
