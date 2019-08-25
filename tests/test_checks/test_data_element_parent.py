import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        ("inside_odoo", 12, []),
        (
            "inside_odoo_8",
            8,
            [
                {
                    "slug": "invalid_data_element_parent",
                    "description": (
                        "Expected `<data>` element to be a direct child of one of "
                        "these elements: openerp"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["data", "foo.xml"], [3])],
                }
            ],
        ),
        ("inside_openerp", 12, []),
        (
            "bare",
            12,
            [
                {
                    "slug": "invalid_data_element_parent",
                    "description": (
                        "Expected `<data>` element to be a direct child of one of "
                        "these elements: openerp, odoo"
                    ),
                    "categories": ["correctness"],
                    "locations": [(["data", "foo.xml"], [2])],
                }
            ],
        ),
    ],
)
def test_data_element_parent(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "data_element_parent",
        (addon_name, "__manifest__.py" if version >= 10 else "__openerp__.py"),
        version,
        expected,
    )
