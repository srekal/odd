import csv
import pathlib

from odd.check import Check
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1, get_model_definition, get_model_type
from odd.utils import split_external_id


class NewModelNoIrModelAccess(Check):
    _handles = {"python_module", "data_file", "demo_file", "xml_record"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._models = {}
        self._access_rules = set()

    def on_python_module(self, python_module):
        for classdef in python_module.module.iter_classdefs():
            if get_model_type(classdef) != "model":
                continue

            model = get_model_definition(classdef, extract_fields=False)

            model_name = model.params.get("_name")
            # In case the model name is e.g. evaluated via function.
            if not isinstance(model_name, str):
                continue
            if model_name and not model.params.get("_inherit"):
                self._models[model_name] = python_module.path, classdef.start_pos
        yield from ()

    def _process_csv(self, path: pathlib.Path):
        with path.open(mode="r") as f:
            for row in csv.DictReader(f):
                external_id = row.get("model_id:id") or row.get("model_id/id")
                if external_id:
                    _, record_id = split_external_id(external_id)
                    self._access_rules.add(record_id)
        yield from ()

    def on_data_file(self, data_file):
        if data_file.path.name.lower() != "ir.model.access.csv":
            return
        yield from self._process_csv(data_file.path)

    def on_demo_file(self, demo_file):
        if demo_file.path.name.lower() != "ir.model.access.csv":
            return
        yield from self._process_csv(demo_file.path)

    def on_xml_record(self, xml_record):
        if xml_record.record_node.attrib["model"] != "ir.model.access":
            return
        for model_el in xml_record.record_node.xpath("./field[@name='model_id']"):
            external_id = model_el.attrib.get("ref")
            if external_id:
                _, record_id = split_external_id(external_id)
                self._access_rules.add(record_id)
        yield from ()

    def on_after(self, addon):
        for model_name, (filename, start_pos) in self._models.items():
            model_external_id = f"model_{model_name.replace('.', '_')}"
            if model_external_id not in self._access_rules:
                yield Issue(
                    "no_ir_model_access_record",
                    f'Model "{model_name}" has no `ir.model.access` records',
                    addon.manifest_path,
                    [Location(filename, [column_index_1(start_pos)])],
                    categories=["correctness", "security"],
                )
