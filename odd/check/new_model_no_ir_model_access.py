import csv

from odd.check import Check
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1, get_model_definition, get_model_type
from odd.xmlutils import split_xml_id


class NewModelNoIrModelAccess(Check):
    def __init__(self):
        super().__init__()
        self._models = {}
        self._access_rules = set()

    def on_python_module(self, addon, filename, module):
        for classdef in module.iter_classdefs():
            if get_model_type(classdef) != "model":
                continue

            model = get_model_definition(classdef, extract_fields=False)

            model_name = model.params.get("_name")
            if model_name and not model.params.get("_inherit"):
                self._models[model_name] = filename, classdef.start_pos
        yield from ()

    def on_path(self, addon, path):
        if (
            not path.is_file()
            or path.name.lower() != "ir.model.access.csv"
            or path not in addon.data_files
        ):
            return

        with path.open(mode="r") as f:
            for row in csv.DictReader(f):
                external_id = row.get("model_id:id") or row.get("model_id/id")
                if external_id:
                    _, record_id = split_xml_id(external_id)
                    self._access_rules.add(record_id)
        yield from ()

    def on_xml_tree(self, addon, filename, tree):
        if filename not in addon.data_files:
            return
        for model_el in tree.xpath(
            "//record[@model='ir.model.access']/field[@name='model_id']"
        ):
            external_id = model_el.attrib.get("ref")
            if external_id:
                _, record_id = split_xml_id(external_id)
                self._access_rules.add(record_id)
        yield from ()

    def on_after(self, addon):
        for model_name, (filename, start_pos) in self._models.items():
            model_external_id = f"model_{model_name.replace('.', '_')}"
            if model_external_id not in self._access_rules:
                yield Issue(
                    "no_ir_model_access_record",
                    f'Model "{model_name}" has no `ir.model.access` records',
                    addon.addon_path,
                    [Location(filename, [column_index_1(start_pos)])],
                    categories=["correctness", "security"],
                )
