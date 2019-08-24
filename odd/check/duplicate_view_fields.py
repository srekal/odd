import collections
import logging

from lxml import etree
from odd.check import Check
from odd.issue import Issue, Location
from odd.utils import split_external_id
from odd.xml_utils import get_view_arch

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


class DuplicateViewFields(Check):
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        record = xml_record.record_node
        if record.attrib["model"] != "ir.ui.view":
            return
        view_xml_id = record.get("id")

        # Skip inherited views.
        inherit_id = record.xpath("./field[@name='inherit_id']")
        if inherit_id and inherit_id[0].attrib.get("ref"):
            return

        # Skip `arch` override in an extending addon.
        if view_xml_id:
            addon_name, _ = split_external_id(view_xml_id)
            if addon_name and addon_name != xml_record.addon.name:
                return

        arch = get_view_arch(record)
        if arch is None:
            _LOG.warning(
                "`ir.ui.view` record has no `arch` field " "in file: %s at line %d",
                xml_record.path,
                record.sourceline,
            )
            return

        children = [c for c in arch.getchildren() if c.tag is not etree.Comment]
        if len(children) != 1:
            _LOG.warning(
                "Unexpected number of children in `ir.ui.view` "
                "`arch` in file: %s at line %d",
                xml_record.path,
                arch.sourceline,
            )
            return

        fields = collections.defaultdict(list)
        for path, line_no in find_fields(arch, ()):
            fields[path].append(line_no)

        for path, line_nos in fields.items():
            if len(line_nos) > 1:
                field_name = path.split("/")[-1]
                yield Issue(
                    "duplicate_view_field",
                    f'"{view_xml_id}" `ir.ui.view` has duplicate field '
                    f'"{field_name}"'
                    if view_xml_id
                    else (f'`ir.ui.view` has duplicate field "{field_name}"'),
                    xml_record.addon.manifest_path,
                    [Location(xml_record.path, [line_no]) for line_no in line_nos],
                    categories=["correctness"],
                )
