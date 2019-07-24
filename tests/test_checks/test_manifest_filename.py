import pytest
import yarl
from odin.checks.addon import ManifestFilename

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "manifest_filename",
            [
                {
                    "slug": "deprecated_manifest_filename",
                    "description": 'Starting with Odoo 10, addon manifest files should be named "__manifest__.py"',
                    "locations": [(["__openerp__.py"], [])],
                    "categories": ["deprecated"],
                    "sources": [
                        yarl.URL(
                            "https://github.com/odoo/odoo/commit/4339196e5231aa734a0154e2f4e88b2e54f27d48"
                        )
                    ],
                }
            ],
        )
    ],
)
def test_manifest_filename(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir,
        "manifest_filename",
        ("__openerp__.py",),
        10,
        ManifestFilename,
        expected,
    )
