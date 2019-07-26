import pytest
from odin.checks.addon import RouteKwargs

from ..common import run_check_test


@pytest.mark.parametrize(
    "addon_name, version, expected",
    [
        (
            "sitemap_in_8",
            8,
            [
                {
                    "slug": "unknown_route_kwarg",
                    "description": 'Controller method `index` has an unknown `route()` keyword argument "sitemap"',
                    "categories": ["correctness"],
                    "locations": [(["controllers", "main.py"], [5])],
                }
            ],
        ),
        ("valid_case", 12, []),
        ("not_route", 12, []),
        ("syntax_error", 12, []),
        ("empty_route", 12, []),
        ("route_on_class", 12, []),
        ("route_no_call", 12, []),
        ("route_wo_http", 12, []),
    ],
)
def test_route_kwargs(test_data_dir, addon_name, version, expected):
    run_check_test(
        test_data_dir,
        "route_kwargs",
        (addon_name, "__manifest__.py"),
        version,
        RouteKwargs,
        expected,
    )
