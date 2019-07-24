import pathlib

from odin.checks import FileCheck
from odin.issue import Issue, Location
from odin.xmlutils import get_model_records, get_root, split_xml_id


MODELS = frozenset(
    (
        "ir.cron",
        "mail.template",
        "ir.rule",
        "account.chart.template",
        "account.account.tag",
        "account.tax.template",
        "account.tax.group",
        "sale.order.template",
        "payment.acquirer",
    )
)


def is_noupdate(record) -> bool:
    parent = record.getparent()
    if parent.tag not in ("data", "odoo", "openerp"):
        raise ValueError(f"Unexpected <record> parent tag: {parent.tag}")
    if "noupdate" in parent.attrib:
        return parent.get("noupdate") == "1"
    else:
        if parent.tag == "data":
            return is_noupdate(parent)
        else:
            return False


class NoUpdate(FileCheck):
    def check(self, filename, addon):
        if filename.suffix.lower() != ".xml" or filename not in addon.data_files:
            return
        for record in get_model_records(get_root(filename)):
            addon_name, xml_id = split_xml_id(record.get("id"))
            if addon_name and addon_name != addon.name:
                continue

            model = record.get("model")
            if model in MODELS and not is_noupdate(record):
                yield Issue(
                    "expected_noupdate_flag",
                    f'`{model}` model records should be declared in a `noupdate="1"` XML data section to allow user modifications',
                    addon.addon_path,
                    [
                        Location(
                            filename, [record.sourceline, record.getparent().sourceline]
                        )
                    ],
                    categories=["correctness"],
                )