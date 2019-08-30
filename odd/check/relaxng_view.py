import functools
import importlib.resources
import logging

import lxml.etree as ET

from odd.check import Check
from odd.issue import Issue, Location
from odd.utils import expand_version_list
from odd.const import SUPPORTED_VERSIONS
from odd.xml_utils import get_root, get_view_arch

_LOG = logging.getLogger(__name__)


VIEW_ELEMENT_VERSION_MAP = expand_version_list(
    {
        ">=8": {"diagram", "search", "tree", "graph", "calendar"},
        ">=8,<=10": {"form", "kanban"},
        ">=8,<=12": {"gantt"},
        ">=9": {"pivot"},
        ">=13": {"activity"},
    },
    *SUPPORTED_VERSIONS,
    result_cls=set,
)


@functools.lru_cache()
def _load_validator(tag: str, version: int) -> ET.RelaxNG:
    module = f"odd.data.relaxng.v{version:d}"
    file_path = "view.rng" if version < 11 else f"{tag:s}_view.rng"
    with importlib.resources.path(module, file_path) as path:
        _LOG.debug("Loading RelaxNG schema from file: %s", path)
        return ET.RelaxNG(get_root(path))


class RelaxNGView(Check):
    _handles = {"xml_record"}

    def on_xml_record(self, xml_record):
        if xml_record.record_node.get("model") != "ir.ui.view":
            return

        # Only works on non-inherited views.
        if xml_record.record_node.xpath('./field[@name="inherit_id"]'):
            return

        # Does not work on QWeb templates.
        if xml_record.record_node.xpath('./field[@name="type" and text() = "qweb"]'):
            return

        arch = get_view_arch(xml_record.record_node)
        if arch is None:
            return

        view_el = next(c for c in arch.iterchildren() if c.tag is not ET.Comment)

        # RelaxNG based validation in <= v10 is only possible for < 7.0 version views.
        if xml_record.addon.version < 11:
            if float(view_el.get("version", "7.0")) >= 7.0:
                return

        # `<form>` and `<kanban>` seem to not be supported in v11+.
        if view_el.tag in ("form", "kanban") and xml_record.addon.version >= 11:
            return

        # `<gantt>` was moved somewhere in v13 (https://git.io/fjxGB).
        if view_el.tag == "gantt" and xml_record.addon.version >= 13:
            return

        # In case it is e.g. `xpath` element in view `arch` override.
        if view_el.tag not in VIEW_ELEMENT_VERSION_MAP[xml_record.addon.version]:
            return

        relaxng = _load_validator(view_el.tag, xml_record.addon.version)
        try:
            relaxng.assert_(view_el)
        except AssertionError:
            last_error = relaxng.error_log.last_error
            yield Issue(
                "view_relaxng_error",
                f'"{view_el.tag}" view does not match the RelaxNG schema: '
                f"{last_error.message}",
                xml_record.addon.manifest_path,
                [Location(xml_record.path, [(last_error.line, last_error.column + 1)])],
                categories=["correctness"],
            )
