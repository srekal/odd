import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "missing_dependency_in_csv",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "sale", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["ir.model.access.csv"], [2])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_menuitem",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "stock", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [14])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_menuitem_groups",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "web", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [14])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_button_action",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "hr", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [10])],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("button_action_self_ref", 12, []),
        (
            "missing_dependency_in_function",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "purchase", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [7])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_function_eval",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "purchase", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [4])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_act_window_groups",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "project", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [8])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_act_window_view_id",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "sale", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [8])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_field_ref",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "website", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [7])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_template_groups",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "account", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [4])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_template_inherit_id",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "payment", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [4])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_view_element_groups",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "event", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["views", "foo.xml"], [11])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_workflow_uid",
            8,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "mrp", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [5])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_workflow_ref",
            8,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "fleet", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [5])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_delete_search",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "mail", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [4])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_delete_id",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "lunch", but it is not in the '
                        "transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [4])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_report_paperformat",
            10,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "point_of_sale", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [10])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_report_groups",
            10,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "some_addon", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [10])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_report_name",
            10,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "sale", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["data", "foo.xml"], [10])],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("ir_set", 8, []),
        ("qweb_files", 12, []),
        ("record_wo_id", 12, []),
        ("missing_dependency_in_addon_with_unknown_dependency", 12, []),
        ("csv_no_external_id_fields", 12, []),
        ("transient_dependency", 12, []),
        (
            "missing_dependency_in_env_ref_call",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "sale", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["models", "foo.py"], [(8, 21)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_env_ref_call_w_raise_if_not_found",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "sale", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["models", "foo.py"], [(8, 30)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_has_group",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "website", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["models", "foo.py"], [(8, 35)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_has_group_model",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "hr", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["models", "foo.py"], [(8, 43)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_user_has_groups",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "project", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["models", "foo.py"], [(8, 43)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        (
            "missing_dependency_in_for_xml_id",
            12,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "account", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["models", "foo.py"], [(8, 60)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("missing_dependency_in_for_xml_id_var", 12, []),
        (
            "missing_dependency_in_for_xml_id_8",
            8,
            [
                {
                    "slug": "missing_dependency",
                    "description": (
                        'Addon references other addon "stock", '
                        "but it is not in the transitive dependency tree"
                    ),
                    "locations": [(["models", "foo.py"], [(8, 65)])],
                    "categories": ["correctness"],
                }
            ],
        ),
    ],
)
def test_missing_dependency(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "missing_dependency",
        (addon_name, "__manifest__.py" if version >= 10 else "__openerp__.py"),
        version,
        expected,
    )
