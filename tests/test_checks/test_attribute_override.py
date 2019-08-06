import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "in_openerp_data",
            9,
            [
                {
                    "slug": "attribute_override",
                    "description": (
                        "`<attribute>` overrides the `class` attribute value, "
                        'consider using `add="..."` or `remove="..."` instead '
                        "of overriding"
                    ),
                    "categories": ["correctness", "maintainability"],
                    "locations": [(["views", "foo.xml"], [11])],
                }
            ],
        ),
        (
            "in_odoo_data",
            12,
            [
                {
                    "slug": "attribute_override",
                    "description": (
                        "`<attribute>` overrides the `class` attribute value, "
                        'consider using `add="..."` or `remove="..."` instead '
                        "of overriding"
                    ),
                    "categories": ["correctness", "maintainability"],
                    "locations": [(["views", "foo.xml"], [11])],
                }
            ],
        ),
        (
            "in_odoo",
            12,
            [
                {
                    "slug": "attribute_override",
                    "description": (
                        "`<attribute>` overrides the `class` attribute value, "
                        'consider using `add="..."` or `remove="..."` instead '
                        "of overriding"
                    ),
                    "categories": ["correctness", "maintainability"],
                    "locations": [(["views", "foo.xml"], [10])],
                }
            ],
        ),
        ("add_in_odoo", 12, []),
        ("remove_in_odoo", 12, []),
    ],
)
def test_attribute_override(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "attribute_override",
        (addon_name, "__manifest__.py" if version >= 10 else "__openerp__.py"),
        version,
        expected,
    )
