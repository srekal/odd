from odd.check import Check
from odd.parso_utils import get_parso_grammar
from odd.issue import Issue, Location

EVAL_ATTRIBUTES = frozenset(
    (
        "eval",
        "context",
        "domain",
        "attrs",
        "statusbar_colors",
        "field_domain",
        "options",
        "t-field-options",
        "t-esc-options",
        "t-raw-options",
        "t-esc",
        "t-value",
        "t-raw",
    )
)

"//record[@context]",
"//record/field[@search]",
"//record/field[@eval]",
"//delete[@search]",
"//function[@eval]",
"//record[@model='ir.ui.view']/field[@name='arch']//*[@attrs]"
"//record[@model='ir.ui.view']/field[@name='arch']//*[@context]"
"//record[@model='ir.ui.view']/field[@name='arch']//*[@domain]"
# <= 9
"//record[@model='ir.ui.view']/field[@name='arch']//*[@statusbar_colors]"

EVAL_ATTR_XPATH = "//*[{attrs}]".format(
    attrs=" or ".join(f"@{attr}" for attr in EVAL_ATTRIBUTES)
)

ATTRIBUTE_TAG_XPATH = "//attribute[{attrs}]".format(
    attrs=" or ".join(f"@name='{attr}'" for attr in EVAL_ATTRIBUTES)
)


def is_view_arch(node) -> bool:
    for a in node.iterancestors():
        if a.tag == "field" and a.attrib.get("name") == "arch":
            return True
    return False


class XMLEval(Check):
    def _check_eval_value(self, addon, filename, node, attr_name, eval_value, grammar):
        if not eval_value or not eval_value.strip():
            return

        ancestor_tags = {a.tag for a in node.iterancestors()}
        # TODO: Ignore `<templates>` in kanban views,
        # since there the expressions use JS.
        if "templates" in ancestor_tags and "kanban" in ancestor_tags:
            return

        module = grammar.parse(eval_value.strip())
        for error in grammar.iter_errors(module):
            description = (
                (
                    f'The Python expression in the "{node.tag}" element "{attr_name}" '
                    f"attribute contains an error: {error.message}"
                )
                if attr_name
                else (
                    f'The Python expression in the "{node.tag}" element contains an '
                    f"error: {error.message}"
                )
            )
            yield Issue(
                "invalid_eval_expression",
                description,
                addon.addon_path,
                [Location(filename, [node.sourceline])],
                categories=["correctness"],
            )

    def on_xml_tree(self, addon, filename, tree):
        grammar = get_parso_grammar(addon)
        if filename not in addon.data_files and filename not in addon.demo_files:
            return

        for node in tree.xpath(EVAL_ATTR_XPATH):
            for attr in EVAL_ATTRIBUTES:
                if attr not in node.attrib:
                    continue
                yield from self._check_eval_value(
                    addon, filename, node, attr, node.attrib[attr], grammar
                )

        # `t-att-*`
        for node in tree.xpath("//*[starts-with(name(@*), 't-att-')]"):
            for attr, attr_value in node.attrib.items():
                if not attr.startswith("t-att-"):
                    continue
                yield from self._check_eval_value(
                    addon, filename, node, attr, attr_value, grammar
                )

        for attribute in tree.xpath(ATTRIBUTE_TAG_XPATH):
            yield from self._check_eval_value(
                addon, filename, attribute, None, attribute.text, grammar
            )
