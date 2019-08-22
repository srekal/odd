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
        "odd.data.relaxng", f"import_xml_{version:d}.rng"
    ) as path:
        _LOG.debug("Loading RelaxNG schema from file: %s", path)
        VERSION_RNG_MAP[version] = ET.RelaxNG(get_root(path))


class RelaxNG(Check):
    def on_xml_tree(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return

        relaxng = VERSION_RNG_MAP[addon.version]

        try:
            relaxng.assert_(tree)
        except AssertionError:
            last_error = relaxng.error_log.last_error
            yield Issue(
                "relaxng_error",
                f"XML file does not match Odoo RelaxNG schema: {last_error.message}",
                addon.addon_path,
                [Location(filename, [(last_error.line, last_error.column + 1)])],
                categories=["correctness"],
            )
