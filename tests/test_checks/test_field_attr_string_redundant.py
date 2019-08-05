import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "redundant_string_12",
            12,
            [
                {
                    "slug": "redundant_field_attribute",
                    "description": 'Redundant field attribute `string="Partner"` for field "partner_id". The same value will be computed by Odoo automatically.',
                    "categories": ["redundancy"],
                    "locations": [(["models", "foo.py"], [(10, 8)])],
                }
            ],
        ),
        (
            "redundant_string_8",
            8,
            [
                {
                    "slug": "redundant_field_attribute",
                    "description": 'Redundant field attribute `string="Name"` for field "name". The same value will be computed by Odoo automatically.',
                    "categories": ["redundancy"],
                    "locations": [(["models", "foo.py"], [(9, 8)])],
                }
            ],
        ),
        ("some_class", 12, []),
        ("unknown_field_class", 8, []),
    ],
)
def test_field_attr_string_redundant(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "field_attr_string_redundant",
        (addon_name, ("__manifest__.py" if version >= 10 else "__openerp__.py")),
        version,
        expected,
    )
