from odd.check import Check
from odd.parso_utils import get_parso_grammar


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
    )
)

EVAL_ATTR_XPATH = "//*[{attrs}]".format(
    attrs=" or ".join(f"@{attr}" for attr in EVAL_ATTRIBUTES)
)

ATTRIBUTE_TAG_XPATH = "//attribute[{attrs}]".format(
    attrs=" or ".join(f"@name='{attr}'" for attr in EVAL_ATTRIBUTES)
)


class XMLEval(Check):
    def _check_eval_value(self, addon, filename, node, grammar, eval_value):
        if not eval_value or not eval_value.strip():
            return
        module = grammar.parse(eval_value.strip())
        issues = list(grammar.iter_errors(module))
        if issues:
            print(
                filename,
                node.sourceline,
                node.tag,
                module.get_code(),
                [issue.message for issue in issues],
            )

    def on_xml_tree(self, addon, filename, tree):
        grammar = get_parso_grammar(addon)
        if filename not in addon.data_files and filename not in addon.demo_files:
            return

        for node in tree.xpath(EVAL_ATTR_XPATH):
            for attr in EVAL_ATTRIBUTES:
                if attr not in node.attrib:
                    continue
                self._check_eval_value(
                    addon, filename, node, grammar, node.attrib[attr]
                )

        for attribute in tree.xpath(ATTRIBUTE_TAG_XPATH):
            self._check_eval_value(addon, filename, attribute, grammar, attribute.text)

        yield from ()
