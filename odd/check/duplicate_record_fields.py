import collections

from odd.check import Check
from odd.issue import Issue, Location
from odd.xml_utils import get_model_records


def get_fields(record):
    fields = collections.defaultdict(list)
    for field in record.xpath("./field"):
        fields[field.attrib["name"]].append(field.sourceline)
    return fields


class DuplicateRecordFields(Check):
    def on_xml_tree(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for record in get_model_records(tree):
            record_fields = get_fields(record)
            for field_name, line_nos in record_fields.items():
                model, record_id = record.attrib["model"], record.attrib["id"]
                if len(line_nos) > 1:
                    yield Issue(
                        "duplicate_record_field",
                        f'`{model}` record "{record_id}" has duplicated values '
                        f'for field "{field_name}"',
                        addon.addon_path,
                        [Location(filename, [line_no]) for line_no in line_nos],
                        categories=["correctness", "maintainability"],
                    )
