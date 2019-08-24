from odd.check import Check
from odd.issue import Issue, Location


def collect_fields(record):
    fields = {}
    for field in record.xpath(".//field"):
        attribs = dict(field.attrib)
        field_name = attribs.pop("name")
        line_no = field.sourceline
        if field.text is not None:
            fields[field_name] = field.text, line_no
        else:
            fields[field_name] = attribs, line_no

    return fields


class IrCronStateCode(Check):
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        if (
            xml_record.addon.version < 11
            or xml_record.record_node.get("model") != "ir.cron"
        ):
            return

        record = xml_record.record_node
        data = collect_fields(record)
        code, code_line_no = data.get("code", (None, None))
        state, state_line_no = data.get("state", (None, None))
        if code and not state:
            yield Issue(
                "incorrect_cron_record",
                f"`ir.cron` record \"{record.attrib['id']}\" has `code` set, "
                f"but no `state` set - code will not be executed when the "
                f"cron job runs",
                xml_record.addon.manifest_path,
                [Location(xml_record.path, [code_line_no])],
                categories=["correctness"],
            )
        elif code and state != "code":
            yield Issue(
                "incorrect_cron_record",
                f"`ir.cron` record \"{record.attrib['id']}\" has `code` set, "
                f'but `state` is not "code" - code will not be executed '
                f"when the cron job runs",
                xml_record.addon.manifest_path,
                [
                    Location(xml_record.path, [code_line_no]),
                    Location(xml_record.path, [state_line_no]),
                ],
                categories=["correctness"],
            )
        elif not code and state == "code":
            yield Issue(
                "incorrect_cron_record",
                f"`ir.cron` record \"{record.attrib['id']}\" has `state` set "
                f'to "code", but `code` is not set',
                xml_record.addon.manifest_path,
                [Location(xml_record.path, [state_line_no])],
                categories=["correctness"],
            )
