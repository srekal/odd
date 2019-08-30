import importlib.resources
import logging

import lxml.etree as ET
from odd.check import Check
from odd.const import SUPPORTED_VERSIONS
from odd.issue import Issue, Location
from odd.xml_utils import get_root


_LOG = logging.getLogger(__name__)


VERSION_RNG_MAP = {}
for version in SUPPORTED_VERSIONS:
    with importlib.resources.path(
        f"odd.data.relaxng.v{version:d}", f"import_xml.rng"
    ) as path:
        _LOG.debug("Loading RelaxNG schema from file: %s", path)
        VERSION_RNG_MAP[version] = ET.RelaxNG(get_root(path))


class RelaxNG(Check):
    _handles = {"xml_tree"}

    def on_xml_tree(self, xml_tree):
        relaxng = VERSION_RNG_MAP[xml_tree.addon.version]

        try:
            relaxng.assert_(xml_tree.tree_node)
        except AssertionError:
            last_error = relaxng.error_log.last_error
            yield Issue(
                "relaxng_error",
                f"XML file does not match Odoo RelaxNG schema: {last_error.message}",
                xml_tree.addon.manifest_path,
                [Location(xml_tree.path, [(last_error.line, last_error.column + 1)])],
                categories=["correctness"],
            )
