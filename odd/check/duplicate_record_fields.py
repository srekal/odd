import collections

from odd.check import Check
from odd.issue import Issue, Location


def get_fields(record):
    fields = collections.defaultdict(list)
    for field in record.xpath("./field"):
        fields[field.attrib["name"]].append(field.sourceline)
    return fields


class DuplicateRecordFields(Check):
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        record = xml_record.record_node
        record_fields = get_fields(record)
        for field_name, line_nos in record_fields.items():
            model, record_id = record.attrib["model"], record.get("id")
            if len(line_nos) > 1:
                yield Issue(
                    "duplicate_record_field",
                    f'`{model}` record "{record_id}" has duplicated values '
                    f'for field "{field_name}"'
                    if record_id
                    else (
                        f"`{model}` record has duplicated values "
                        f'for field "{field_name}"'
                    ),
                    xml_record.addon.manifest_path,
                    [Location(xml_record.path, [line_no]) for line_no in line_nos],
                    categories=["correctness", "maintainability"],
                )
