import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        (
            "no_ir_model_access",
            [
                {
                    "slug": "no_ir_model_access_record",
                    "description": ('Model "foo" has no `ir.model.access` records'),
                    "locations": [(["models", "foo.py"], [(4, 1)])],
                    "categories": ["correctness", "security"],
                }
            ],
        ),
        ("has_ir_model_access_in_csv", []),
        ("has_ir_model_access_in_xml", []),
        ("no_ir_model_access_transient", []),
        ("no_ir_model_access_abstract", []),
        ("inherit_no_ir_model_access", []),
        (
            "csv_not_included",
            [
                {
                    "slug": "no_ir_model_access_record",
                    "description": ('Model "foo" has no `ir.model.access` records'),
                    "locations": [(["models", "foo.py"], [(4, 1)])],
                    "categories": ["correctness", "security"],
                }
            ],
        ),
        (
            "xml_not_included",
            [
                {
                    "slug": "no_ir_model_access_record",
                    "description": ('Model "foo" has no `ir.model.access` records'),
                    "locations": [(["models", "foo.py"], [(4, 1)])],
                    "categories": ["correctness", "security"],
                }
            ],
        ),
        ("has_ir_model_access_in_csv_full_external_id", []),
        ("has_ir_model_access_in_xml_full_external_id", []),
        ("has_ir_model_access_in_csv_different_notation", []),
        (
            "other_model_csv",
            [
                {
                    "slug": "no_ir_model_access_record",
                    "description": ('Model "foo" has no `ir.model.access` records'),
                    "locations": [(["models", "foo.py"], [(4, 1)])],
                    "categories": ["correctness", "security"],
                }
            ],
        ),
    ],
)
def test_new_model_no_ir_model_access(test_data_dir, addon_name, expected):
    run_check_test(
        test_data_dir,
        "new_model_no_ir_model_access",
        (addon_name, "__manifest__.py"),
        12,
        expected,
    )
