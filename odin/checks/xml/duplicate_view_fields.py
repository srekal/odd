import collections
import logging

from lxml import etree

from odin.checks import XMLCheck
from odin.issue import Issue, Location
from odin.xmlutils import get_model_records, split_xml_id, get_view_arch

_LOG = logging.getLogger(__name__)
VIEW_TAGS = frozenset(
    [
        "tree",
        "form",
        "graph",
        "pivot",
        "kanban",
        "calendar",
        "search",
        # These views don't have `<field>`:
        # "gantt", "diagram", "dashboard", "cohort".
    ]
)
# These tags can have `<field>` inside,
FIELD_TAGS = frozenset(["templates", "button"])


def find_fields(el, path):
    result = []
    for child in el.iterchildren():
        child_tag = child.tag
        if child.tag == "field":
            field_name = child.attrib["name"]
            result.append(("/".join((*path, field_name)), child.sourceline))
            child_tag = f"field[{field_name}]"

        new_path = path
        if child.tag in VIEW_TAGS or child.tag in FIELD_TAGS or child.tag != child_tag:
            new_path = (*path, child_tag)
        result.extend(find_fields(child, new_path))
    return result


class DuplicateViewFields(XMLCheck):
    def check(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for record in get_model_records(tree):
            view_xml_id = record.attrib["id"]

            # Skip inherited views.
            inherit_id = record.xpath("./field[@name='inherit_id']")
            if inherit_id and inherit_id[0].attrib.get("ref"):
                continue

            # Skip `arch` override in an extending addon.
            addon_name, _ = split_xml_id(view_xml_id)
            if addon_name and addon_name != addon.name:
                continue

            arch = get_view_arch(record)
            if arch is None:
                _LOG.warning(
                    "`ir.ui.view` record has no `arch` field " "in file: %s at line %d",
                    filename,
                    record.sourceline,
                )
                continue

            children = [c for c in arch.getchildren() if not c.tag is etree.Comment]
            if len(children) != 1:
                _LOG.warning(
                    "Unexpected number of children in `ir.ui.view` "
                    "`arch` in file: %s at line %d",
                    filename,
                    arch.sourceline,
                )
                continue

            fields = collections.defaultdict(list)
            for path, line_no in find_fields(arch, ()):
                fields[path].append(line_no)

            for path, line_nos in fields.items():
                if len(line_nos) > 1:
                    field_name = path.split("/")[-1]
                    yield Issue(
                        "duplicate_view_field",
                        f'"{view_xml_id}" `ir.ui.view` has duplicate field "{field_name}"',
                        addon.addon_path,
                        [Location(filename, [line_no]) for line_no in line_nos],
                        categories=["correctness"],
                    )
