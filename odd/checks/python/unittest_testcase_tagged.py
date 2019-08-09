from odd.checks import PythonCheck
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1, extract_func_name, get_bases, get_imports
from odd.utils import odoo_commit_url


class UnitTestTestCaseTagged(PythonCheck):
    def check(self, addon, filename, module):
        if addon.version < 12 or not filename.name.startswith("test_"):
            return

        imports = set()
        for imp in get_imports(module):
            from_part = ".".join(imp.from_names)
            if from_part:
                imports.update((from_part, n) for n in imp.names)
            else:
                imports.update(imp.names)

        for classdef in module.iter_classdefs():
            bases = get_bases(classdef.get_super_arglist())
            is_test_case = (
                ("unittest", "TestCase") in bases and "unittest" in imports
            ) or (("TestCase",) in bases and ("unittest", "TestCase") in imports)
            if not is_test_case:
                continue

            tagged = False
            for decorator in classdef.get_decorators():
                if extract_func_name(decorator)[-1] == "tagged":
                    tagged = True
                    break
            if not tagged:
                yield Issue(
                    "unittest_testcase_not_tagged",
                    f"`unittest.TestCase` subclass `{classdef.name.value}` is not "
                    f"decorated with `@tagged()`, it will not be picked up by Odoo "
                    f"test runner",
                    addon.addon_path,
                    [Location(filename, [column_index_1(classdef.start_pos)])],
                    categories=["correctness"],
                    sources=[
                        odoo_commit_url("b356b190338e3ee032b9e3a7f670f76468965006")
                    ],
                )
