from odd.check import Check
from odd.issue import Issue, Location
from odd.utils import split_external_id

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


class NoUpdate(Check):
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        record = xml_record.record_node
        record_id = record.get("id")
        if (
            not record_id
            or xml_record.noupdate
            or xml_record.path not in xml_record.addon.data_files
        ):
            return

        addon_name, _ = split_external_id(record_id)
        if addon_name and addon_name != xml_record.addon.name:
            return

        model = record.attrib["model"]
        if model in MODELS:
            yield Issue(
                "expected_noupdate_flag",
                f'`{model}` model records should be declared in a `noupdate="1"` '
                f"XML data element to allow user modifications",
                xml_record.addon.manifest_path,
                [
                    Location(
                        xml_record.path,
                        [record.sourceline, record.getparent().sourceline],
                    )
                ],
                categories=["correctness"],
            )
