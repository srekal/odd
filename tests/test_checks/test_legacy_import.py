import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "from_openerp_import_models",
            10,
            [
                {
                    "slug": "legacy_import",
                    "description": "Legacy import `openerp`",
                    "locations": [(["models", "foo.py"], [(1, 1)])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        ("from_openerp_import_models", 9, []),
        (
            "import_openerp",
            10,
            [
                {
                    "slug": "legacy_import",
                    "description": "Legacy import `openerp`",
                    "locations": [(["models", "foo.py"], [(1, 1)])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        ("import_openerp", 9, []),
        (
            "from_odoo_import_osv",
            12,
            [
                {
                    "slug": "legacy_import",
                    "description": "Legacy import `osv`",
                    "locations": [(["models", "foo.py"], [(1, 1)])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        (
            "from_openerp_addons_import_foo",
            10,
            [
                {
                    "slug": "legacy_import",
                    "description": "Legacy import `openerp`",
                    "locations": [(["models", "foo.py"], [(2, 1)])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        ("from_openerp_addons_import_foo", 9, []),
        (
            "import_odoo_osv",
            10,
            [
                {
                    "slug": "legacy_import",
                    "description": "Legacy import `osv`",
                    "locations": [(["models", "foo.py"], [(1, 1)])],
                    "categories": ["deprecated"],
                }
            ],
        ),
        (
            "from_odoo_osv_import_osv",
            10,
            [
                {
                    "slug": "legacy_import",
                    "description": "Legacy import `osv`",
                    "locations": [(["models", "foo.py"], [(1, 1)])],
                    "categories": ["deprecated"],
                }
            ],
        ),
    ],
)
def test_legacy_import(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "legacy_import",
        (addon_name, "__manifest__.py"),
        version,
        expected,
    )
