import pytest

from odin.xmlutils import get_xpath_expr_target_element


@pytest.mark.parametrize(
    "xpath_expr, expected",
    [
        (".", None),
        ("//div", "div"),
        ("//div[@id='snippet_options']", "div"),
        ("//field[@name='product_return_moves']/tree", "tree"),
        (
            "//t[@t-name='JournalBodyBankCash']"
            "//div[hasclass('o_kanban_primary_right')]",
            "div",
        ),
        ("//label[@for='module_sale_quotation_builder']/following::div", "div"),
    ],
)
def test_get_xpath_expr_target_element(xpath_expr, expected):
    assert get_xpath_expr_target_element(xpath_expr) == expected
