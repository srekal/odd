import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "new_model_no_description_12",
            12,
            [
                {
                    "slug": "no_model_description",
                    "description": ('Model "foo" has no `_description` set'),
                    "locations": [(["models", "foo.py"], [(4, 1)])],
                    "categories": ["correctness"],
                    "sources": [
                        "https://github.com/odoo/odoo/blob"
                        "/ff9ddfdacc9581361b555fd5f69e2da61800acad"
                        "/odoo/models.py#L529"
                    ],
                }
            ],
        ),
        ("inherit_no_description_12", 12, []),
        (
            "new_model_no_description_11",
            11,
            [
                {
                    "slug": "no_model_description",
                    "description": ('Model "foo" has no `_description` set'),
                    "locations": [(["models", "foo.py"], [(4, 1)])],
                    "categories": ["future-warning"],
                    "sources": [
                        "https://github.com/odoo/odoo/blob"
                        "/ff9ddfdacc9581361b555fd5f69e2da61800acad"
                        "/odoo/models.py#L529"
                    ],
                }
            ],
        ),
        ("simple_class_12", 12, []),
        ("abstract_component", 12, []),
    ],
)
def test_new_model_description(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "new_model_description",
        (addon_name, "__manifest__.py"),
        version,
        expected,
    )
