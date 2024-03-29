import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        ("lambda_in_default", 12, []),
        ("model_specific_attr", 12, []),
        (
            "typo_1",
            12,
            [
                {
                    "slug": "unknown_field_attribute",
                    "description": (
                        'Unknown field attribute "String" for field type "Many2one"'
                    ),
                    "categories": ["correctness"],
                    "locations": [(["models", "foo.py"], [(10, 9)])],
                }
            ],
        ),
        (
            "deprecated_1",
            12,
            [
                {
                    "slug": "deprecated_field_attribute",
                    "description": (
                        'Deprecated field attribute "size" for field type "Char"'
                    ),
                    "categories": ["deprecated"],
                    "locations": [(["models", "foo.py"], [(9, 9)])],
                }
            ],
        ),
        ("oldname", 12, []),
        (
            "oldname",
            13,
            [
                {
                    "slug": "deprecated_field_attribute",
                    "description": (
                        'Deprecated field attribute "oldname" for field type "Char"'
                    ),
                    "categories": ["deprecated"],
                    "locations": [(["models", "foo.py"], [(9, 9)])],
                }
            ],
        ),
        (
            "direct_import",
            12,
            [
                {
                    "slug": "unknown_field_attribute",
                    "description": (
                        'Unknown field attribute "translate" for field type '
                        '"Many2one"'
                    ),
                    "categories": ["correctness"],
                    "locations": [(["models", "foo.py"], [(11, 9)])],
                }
            ],
        ),
        (
            "full_import_path",
            12,
            [
                {
                    "slug": "unknown_field_attribute",
                    "description": (
                        'Unknown field attribute "selection" for field type '
                        '"Many2one"'
                    ),
                    "categories": ["correctness"],
                    "locations": [(["models", "foo.py"], [(10, 9)])],
                }
            ],
        ),
        (
            "unknown_field_type",
            12,
            [
                {
                    "slug": "unknown_field_type",
                    "description": 'Unknown field type "Foobar"',
                    "categories": ["correctness"],
                    "locations": [(["models", "foo.py"], [(8, 11)])],
                }
            ],
        ),
        ("no_model", 12, []),
        ("compute_field", 12, []),
        ("related_field", 12, []),
        ("django_fields", 12, []),
        ("no_fields", 12, []),
        ("very_long_import", 12, []),
        (
            "image_field",
            12,
            [
                {
                    "slug": "unknown_field_type",
                    "description": 'Unknown field type "Image"',
                    "categories": ["correctness"],
                    "locations": [(["models", "foo.py"], [(8, 17)])],
                }
            ],
        ),
        ("image_field", 13, []),
        (
            "many2one_reference_field",
            12,
            [
                {
                    "slug": "unknown_field_type",
                    "description": 'Unknown field type "Many2oneReference"',
                    "categories": ["correctness"],
                    "locations": [(["models", "foo.py"], [(14, 14)])],
                }
            ],
        ),
        ("many2one_reference_field", 13, []),
        (
            "renamed_attribute_select",
            10,
            [
                {
                    "slug": "renamed_field_attribute",
                    "description": 'Field attribute "select" was renamed to "index"',
                    "categories": ["deprecated"],
                    "locations": [(["models", "foo.py"], [(9, 9)])],
                }
            ],
        ),
        ("depends_context_attribute", 13, []),
    ],
)
def test_field_attrs(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir, "field_attrs", (addon_name, "__manifest__.py"), version, expected
    )
