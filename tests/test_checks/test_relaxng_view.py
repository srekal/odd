import pytest

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "typo_element_name",
            12,
            [
                {
                    "slug": "view_relaxng_error",
                    "description": (
                        '"tree" view does not match the RelaxNG schema: '
                        "Element tree has extra content: fiedl"
                    ),
                    "locations": [(["views", "foo.xml"], [(9, 1)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("typo_element_name_extension", 12, []),
        ("qweb_template", 12, []),
        ("no_arch", 12, []),
        ("other_model", 12, []),
        ("form_view", 12, []),
        ("gantt_view", 13, []),
        (
            "gantt_view",
            12,
            [
                {
                    "slug": "view_relaxng_error",
                    "description": (
                        '"gantt" view does not match the RelaxNG schema: '
                        "Element gantt failed to validate attributes"
                    ),
                    "locations": [(["views", "foo.xml"], [(8, 1)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("arch_override", 12, []),
        (
            "view_6_1",
            10,
            [
                {
                    "slug": "view_relaxng_error",
                    "description": (
                        '"tree" view does not match the RelaxNG schema: '
                        "Element tree has extra content: fiedl"
                    ),
                    "locations": [(["views", "foo.xml"], [(9, 1)])],
                    "categories": ["correctness"],
                }
            ],
        ),
        ("view_7_0", 10, []),
    ],
)
def test_relaxng_view(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "relaxng_view",
        (addon_name, "__manifest__.py"),
        version,
        expected,
    )
