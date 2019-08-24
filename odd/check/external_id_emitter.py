import ast
import collections
import dataclasses
import typing

import parso

from odd.addon import Addon
from odd.artifact import Artifact
from odd.check import Check
from odd.check.python_emitter import PythonModule
from odd.const import SUPPORTED_VERSIONS, UNKNOWN
from odd.issue import Location
from odd.parso_utils import (
    Call,
    column_index_1,
    get_string_node_value,
    iter_calls,
    walk,
)
from odd.utils import (
    expand_version_list,
    remove_old_style_format,
    split_external_id,
    split_groups,
)
from odd.xml_utils import get_view_arch
from odd.yaml_utils import YamlTag, line_column_index_1, load

XML_OPERATION_VERSION_MAP = expand_version_list(
    {
        ">=8": [
            "record",
            "menuitem",
            "act_window",
            "report",
            "template",
            "delete",
            "function",
        ],
        "==8": ["ir_set"],
        "<=10": ["workflow"],
    },
    *SUPPORTED_VERSIONS,
    result_cls=list,
)
KNOWN_FIELD_MODELS = {
    "ir.rule": {"model_id": "ir.model"},
    "ir.ui.view": {"inherit_id": "ir.ui.view"},
}


@dataclasses.dataclass
class ExternalIDReference(Artifact):
    addon: Addon
    addon_name: typing.Optional[typing.Union[str, object]]
    record_id: str
    model: typing.Union[str, object]
    location: Location


@dataclasses.dataclass
class ExternalID(ExternalIDReference):
    ...


def _model_record_id(model: str) -> str:
    return f"model_{model.replace('.', '_')}"


def _field_record_id(model: str, field_name: str) -> str:
    return f"field_{model.replace('.', '_')}__{field_name}"


def _ref(
    addon, filename, position, external_id, model, unknown_addon=False
) -> ExternalIDReference:
    addon_name, record_id = split_external_id(external_id)
    return ExternalIDReference(
        addon,
        UNKNOWN if unknown_addon else addon_name,
        record_id,
        model,
        Location(filename, [position]),
    )


def _ref_or_def(
    addon, filename, position, external_id, model
) -> typing.Union[ExternalID, ExternalIDReference]:
    addon_name, record_id = split_external_id(external_id)
    cls_ = ExternalIDReference
    if not addon_name or addon_name == addon.name:
        cls_ = ExternalID
    return cls_(addon, addon_name, record_id, model, Location(filename, [position]))


def _model_ref(addon, filename, position, model_name: str) -> ExternalIDReference:
    return _ref(
        addon,
        filename,
        position,
        _model_record_id(model_name),
        "ir.model",
        unknown_addon=True,
    )


def _ref_getter(_, call: Call) -> typing.Generator[str, None, None]:
    if call.args:
        if isinstance(call.args[0], str) and call.args[0]:
            yield call.args[0]


def _user_has_groups_getter(_, call: Call) -> typing.Generator[str, None, None]:
    if call.args:
        if isinstance(call.args[0], str) and call.args[0]:
            yield from split_groups(call.args[0])


def _for_xml_id_getter(
    addon_version: int, call: Call
) -> typing.Generator[str, None, None]:
    # `for_xml_id(cr, uid, "addon_name", "record_id")` possible in v8 and v9.
    addon_name, record_id = "", ""
    if addon_version < 10 and len(call.args) >= 4:
        addon_name, record_id = call.args[2:4]
    elif len(call.args) >= 2:
        addon_name, record_id = call.args[:2]

    if (
        addon_name
        and record_id
        and isinstance(addon_name, str)
        and isinstance(record_id, str)
    ):
        yield f"{addon_name}.{record_id}"


class ExternalIDEmitter(Check):
    _handles = {"xml_tree", "data_file", "demo_file", "python_module", "csv_row"}
    _emits = {"external_id", "external_id_reference", "python_module"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._grammar_2 = parso.load_grammar(version="2.7")
        self._grammar_3 = parso.load_grammar(version="3.5")

        # A cache map of `pathlib.Path` -> {external IDs field names} to not compute
        # the field names repeatedly for each row in a file.
        self._csv_external_id_fields = collections.defaultdict(set)

    def _get_grammar(self, addon: Addon) -> parso.Grammar:
        return self._grammar_2 if addon.version < 11 else self._grammar_3

    def _extract_xml_record(self, addon, filename, tree):
        # <record> operation.
        for record in tree.xpath("//record"):
            record_model, record_id = record.attrib["model"], record.get("id")
            if record_model:
                yield _model_ref(addon, filename, record.sourceline, record_model)
            if record_id:
                yield _ref_or_def(
                    addon, filename, record.sourceline, record_id, record_model
                )

            # <field> operation.
            for field in record.iterchildren(tag="field"):
                field_name = field.attrib["name"]

                field_external_id = _field_record_id(record_model, field_name)
                yield ExternalIDReference(
                    addon,
                    UNKNOWN,
                    field_external_id,
                    "ir.model.fields",
                    Location(filename, field.sourceline),
                )

                ref = field.get("ref")
                if ref:
                    ref_model = KNOWN_FIELD_MODELS.get(record_model, {}).get(
                        field_name, UNKNOWN
                    )
                    yield _ref(addon, filename, field.sourceline, ref, ref_model)

                for attr_name in ("eval", "search"):
                    yield from self._get_ref_from_eval(
                        addon, filename, field.sourceline, field.get(attr_name)
                    )

            # View-specific tags.
            if record_model != "ir.ui.view":
                continue

            arch = get_view_arch(record)
            if arch is None:
                continue

            for button in arch.xpath(".//button[@type='action' and @name]"):
                button_name = button.get("name")
                if button_name:
                    yield _ref(
                        addon,
                        filename,
                        button.sourceline,
                        remove_old_style_format(button_name),
                        "ir.ui.view",
                    )

            for el in arch.xpath(".//*[@groups]"):
                groups = el.get("groups")
                for group in split_groups(groups):
                    yield _ref(addon, filename, el.sourceline, group, "res.groups")

    def _extract_xml_menuitem(self, addon, filename, tree):
        # <menuitem> shortcut.
        for menuitem in tree.xpath("//menuitem"):
            yield _ref_or_def(
                addon,
                filename,
                menuitem.sourceline,
                menuitem.attrib["id"],
                "ir.ui.menu",
            )
            parent = menuitem.get("parent")
            if parent:
                yield _ref(addon, filename, menuitem.sourceline, parent, "ir.ui.menu")

            action = menuitem.get("action")
            if action:
                yield _ref(
                    addon,
                    filename,
                    menuitem.sourceline,
                    action,
                    "ir.actions.act_window",
                )

            groups = menuitem.get("groups")
            if groups:
                for group in split_groups(groups):
                    yield _ref(
                        addon, filename, menuitem.sourceline, group, "res.groups"
                    )

    def _extract_xml_act_window(self, addon, filename, tree):
        # <act_window> shortcut.
        for act_window in tree.xpath("//act_window"):
            yield _ref_or_def(
                addon,
                filename,
                act_window.sourceline,
                act_window.attrib["id"],
                "ir.actions.act_window",
            )

            groups = act_window.get("groups")
            if groups:
                for group in split_groups(groups):
                    yield _ref(
                        addon, filename, act_window.sourceline, group, "res.groups"
                    )

            view_id = act_window.get("view_id")
            if view_id:
                yield _ref(
                    addon, filename, act_window.sourceline, view_id, "ir.ui.view"
                )

            res_model = act_window.get("res_model")
            if res_model:
                yield _model_ref(addon, filename, act_window.sourceline, res_model)

            src_model = act_window.get("src_model")
            if src_model:
                yield _model_ref(addon, filename, act_window.sourceline, src_model)

    def _extract_xml_report(self, addon, filename, tree):
        # <report> shortcut.
        for report in tree.xpath("//report"):
            # TODO: `name`, `file`?
            yield _ref_or_def(
                addon,
                filename,
                report.sourceline,
                report.attrib["id"],
                "ir.actions.report",
            )

            name = report.get("name")
            if name and "rml" not in report.attrib:
                yield _ref(addon, filename, report.sourceline, name, "ir.ui.view")

            paperformat_id = report.get("paperformat")
            if paperformat_id and addon.version > 8:
                yield _ref(
                    addon,
                    filename,
                    report.sourceline,
                    paperformat_id,
                    "report.paperformat",
                )

            model = report.get("model")
            if model:
                yield _model_ref(addon, filename, report.sourceline, model)

            groups = report.get("groups")
            if groups:
                for group in split_groups(groups):
                    yield _ref(addon, filename, report.sourceline, group, "res.groups")

    def _extract_xml_template(self, addon, filename, tree):
        # <template> shortcut.
        for template in tree.xpath("//template"):
            template_id = template.get("id")
            if template_id:
                yield _ref_or_def(
                    addon, filename, template.sourceline, template_id, "ir.ui.view"
                )

            inherit_id = template.get("inherit_id")
            if inherit_id:
                yield _ref(
                    addon, filename, template.sourceline, inherit_id, "ir.ui.view"
                )

            groups = template.get("groups")
            if groups:
                for group in split_groups(groups):
                    yield _ref(
                        addon, filename, template.sourceline, group, "res.groups"
                    )

    def _extract_xml_delete(self, addon, filename, tree):
        # <delete> operation.
        for delete in tree.xpath("//delete"):
            search = delete.get("search")
            if search:
                yield from self._get_ref_from_eval(
                    addon, filename, delete.sourceline, search
                )

            model = delete.get("model")
            if model:
                yield _model_ref(addon, filename, delete.sourceline, model)

            record_id = delete.get("id")
            if record_id:
                yield _ref(addon, filename, delete.sourceline, record_id, model)

    def _extract_xml_function(self, addon, filename, tree):
        # <function> operation.
        for function in tree.xpath("//function"):
            model = function.get("model")
            if model:
                yield _model_ref(addon, filename, function.sourceline, model)

            eval_ = function.get("eval")
            if eval_:
                yield from self._get_ref_from_eval(
                    addon, filename, function.sourceline, eval_
                )

            for value in function.iterchildren(tag="value"):
                eval_ = value.get("eval")
                if eval_:
                    yield from self._get_ref_from_eval(
                        addon, filename, value.sourceline, eval_
                    )

    def _extract_xml_workflow(self, addon, filename, tree):
        # <workflow> operation (removed in v11).
        for workflow in tree.xpath("//workflow"):
            model, ref = workflow.get("model"), workflow.get("ref")
            if model:
                yield _model_ref(addon, filename, workflow.sourceline, model)
            if model and ref:
                yield _ref(addon, filename, workflow.sourceline, ref, model)

            uid = workflow.get("uid")
            if uid:
                yield _ref(addon, filename, workflow.sourceline, uid, "res.users")

    def _extract_xml_ir_set(self, addon, filename, tree):
        # <ir_set> operation (removed in v9).
        for ir_set in tree.xpath("//ir_set"):
            for field in ir_set.iterchildren(tag="field"):
                eval_ = field.get("eval")
                if not eval_:
                    continue

                if field.get("name") == "models":
                    eval_value = field.get("eval")
                    if eval_value:
                        for model in ast.literal_eval(eval_value):
                            yield _model_ref(addon, filename, field.sourceline, model)

                yield from self._get_ref_from_eval(
                    addon, filename, field.sourceline, eval_
                )

    def _extract_path_yml(self, addon, path):
        for entry in load(path):
            if isinstance(entry, str):
                continue
            for key, val in entry.items():
                if isinstance(key, YamlTag) and key.tag in ("record", "python"):
                    model = key.get("model")
                    record_id = key.get("id")

                    if model:
                        yield _model_ref(
                            addon, path, line_column_index_1(key.start_pos), model
                        )

                    if model and record_id:
                        yield _ref(
                            addon,
                            path,
                            line_column_index_1(key.start_pos),
                            record_id,
                            model,
                        )
                    if key.tag == "python":
                        module = self._get_grammar(addon).parse(val)
                        # FIXME: The position will be wrong here.
                        yield PythonModule(addon, path, module)
                # TODO: Support other tags? I haven't seen them being used, though.

    def _get_ref_from_eval(self, addon, filename, position, eval_value):
        if not eval_value or eval_value in ("True", "False", "1", "0"):
            return

        # TODO: Handle cases like these:
        # <function model="stock.picking" name="action_confirm">
        #    <value model="stock.picking" eval="[
        #        obj().env.ref('stock.outgoing_shipment_main_warehouse').id,
        #    ]"/>
        # </function>

        module = self._get_grammar(addon).parse(eval_value)
        for node in walk(module):
            if (
                node.type == "atom_expr"
                and len(node.children) == 2
                and node.children[0].type == "name"
                and node.children[0].value == "ref"
                and node.children[1].type == "trailer"
                and len(node.children[1].children) == 3
                and node.children[1].children[0].type == "operator"
                and node.children[1].children[0].value == "("
                and node.children[1].children[2].type == "operator"
                and node.children[1].children[2].value == ")"
                and node.children[1].children[1].type == "string"
            ):
                ref = get_string_node_value(node.children[1].children[1])
                if ref:
                    yield _ref(addon, filename, position, ref, UNKNOWN)

    def _check_file(self, addon_path):
        # NOTE: XML is already handled by `xml_tree`.
        if addon_path.path.suffix.lower() == ".yml" and addon_path.addon.version < 12:
            yield from self._extract_path_yml(addon_path.addon, addon_path.path)

    def on_xml_tree(self, xml_tree):
        for op in XML_OPERATION_VERSION_MAP[xml_tree.addon.version]:
            yield from getattr(self, f"_extract_xml_{op}")(
                xml_tree.addon, xml_tree.path, xml_tree.tree_node
            )

    on_data_file = on_demo_file = _check_file

    def on_python_module(self, python_module):
        addon_version = python_module.addon.version

        def _check_call(call: Call, call_end_parts, ref_values_getter, model=UNKNOWN):
            for end_part in call_end_parts:
                if call.names[-len(end_part) :] != end_part:
                    continue

                position = column_index_1(call.start_pos)
                for ref_value in ref_values_getter(addon_version, call):
                    yield _ref(
                        python_module.addon,
                        python_module.path,
                        position,
                        ref_value,
                        model,
                    )

        # TODO: Add support if external ID was passed via `kwargs`.
        for call in iter_calls(python_module.module):
            for end_parts, ref_getter, model in [
                ([("env", "ref")], _ref_getter, UNKNOWN),
                ([("has_group",)], _ref_getter, "res.groups"),
                ([("user_has_groups",)], _user_has_groups_getter, "res.groups"),
                ([("for_xml_id",)], _for_xml_id_getter, "ir.actions.act_window"),
            ]:
                found = False
                for artifact in _check_call(call, end_parts, ref_getter, model=model):
                    yield artifact
                    found = True

                if found:
                    # We found our match, no point in continuing.
                    break

    def on_csv_row(self, csv_row):
        model = csv_row.path.stem
        addon, path, row = csv_row.addon, csv_row.path, csv_row.row

        yield ExternalIDReference(
            addon, UNKNOWN, _model_record_id(model), "ir.model", Location(path)
        )

        if path not in self._csv_external_id_fields:
            for field_name in row:
                if (
                    field_name.split(":")[-1] == "id"
                    or field_name.split("/")[-1] == "id"
                ):
                    self._csv_external_id_fields[path].add(field_name)

                # Add references to fields from the CSV file header.
                field_external_id = _field_record_id(
                    model,
                    (
                        field_name[:-3]
                        if field_name.endswith((":id", "/id"))
                        else field_name
                    ),
                )
                yield ExternalIDReference(
                    addon,
                    UNKNOWN,
                    field_external_id,
                    "ir.model.fields",
                    Location(path, [1]),
                )

        for field_name in self._csv_external_id_fields[path]:
            # TODO: Add support for KNOWN_FIELD_MODELS.
            external_id = csv_row.row[field_name]
            if not external_id:
                continue
            addon_name, record_id = split_external_id(external_id)
            cls_ = ExternalID if field_name == "id" else ExternalIDReference
            yield cls_(
                csv_row.addon,
                addon_name,
                record_id,
                model if field_name == "id" else UNKNOWN,
                Location(csv_row.path, [csv_row.line_no]),
            )
