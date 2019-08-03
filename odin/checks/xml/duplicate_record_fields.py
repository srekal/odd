import collections

from odin.checks import XMLCheck
from odin.issue import Issue, Location
from odin.xmlutils import get_model_records


def get_fields(record):
    fields = collections.defaultdict(list)
    for field in record.xpath("./field"):
        fields[field.attrib["name"]].append(field.sourceline)
    return fields


class DuplicateRecordFields(XMLCheck):
    def check(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for record in get_model_records(tree):
            record_fields = get_fields(record)
            for field_name, line_nos in record_fields.items():
                model, record_id = record.attrib["model"], record.attrib["id"]
                # TODO: Add support for duplicated fields inside views.
                # if model == "ir.ui.view" and "inherit_id" in record_fields:
                #    continue
                if len(line_nos) > 1:
                    yield Issue(
                        "duplicate_record_field",
                        f'`{model}` record "{record_id}" has duplicated values for field "{field_name}"',
                        addon.addon_path,
                        [Location(filename, [line_no]) for line_no in line_nos],
                        categories=["correctness", "maintainability"],
                    )
