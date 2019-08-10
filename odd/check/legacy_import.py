from odd.check import Check
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1, get_imports


class LegacyImport(Check):
    def on_python_module(self, addon, filename, module):
        version = addon.version

        def issue(module_import, import_name):
            yield Issue(
                "legacy_import",
                f"Legacy import `{import_name}`",
                addon.addon_path,
                [Location(filename, [column_index_1(module_import.start_pos)])],
                categories=["deprecated"],
            )

        for imp in get_imports(module):
            if imp.from_names:
                # from openerp import X
                if version >= 10 and imp.from_names[:1] == ("openerp",):
                    yield from issue(imp, "openerp")

                # from (openerp|odoo).osv import X
                if imp.from_names[:2] in (("openerp", "osv"), ("odoo", "osv")):
                    yield from issue(imp, "osv")
                # from (openerp|odoo) import osv
                elif (
                    imp.from_names[:1] in (("openerp",), ("odoo",))
                    and "osv" in imp.names
                ):
                    yield from issue(imp, "osv")

            else:
                # import openerp
                # import openerp.X
                if version >= 10 and imp.names[:1] == ("openerp",):
                    yield from issue(imp, "openerp")

                # import (openerp|odoo).osv
                if imp.names[:2] in (("openerp", "osv"), ("odoo", "osv")):
                    yield from issue(imp, "osv")
