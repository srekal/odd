import dataclasses

import pytest

from odd.addon import Addon, ManifestPath, parse_manifest
from odd.const import UNKNOWN
from odd.check.path_emitter import AddonPath
from odd.check.python_emitter import (
    FieldDefinitionEmitter,
    ModelDefinitionEmitter,
    PythonEmitter,
)

from ..common import subdict


@pytest.mark.parametrize(
    "addon_name, filename_parts, expected",
    [
        ("simple_addon", ("models", "no_fields.py"), []),
        ("simple_addon", ("models", "django_fields.py"), []),
        ("simple_addon", ("models", "django_fields_2.py"), []),
        (
            "simple_addon",
            ("models", "simple_model_with_field.py"),
            [
                {
                    "name": "bar",
                    "class_name": "Char",
                    "start_pos": (7, 10),
                    "end_pos": (7, 23),
                    "args": [],
                    "kwargs": [],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "simple_model_with_field_one_kwarg.py"),
            [
                {
                    "name": "bar",
                    "class_name": "Char",
                    "start_pos": (7, 10),
                    "end_pos": (9, 5),
                    "args": [],
                    "kwargs": [
                        {
                            "name": "string",
                            "value": "Bar",
                            "start_pos": (8, 8),
                            "end_pos": (8, 20),
                        }
                    ],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "simple_model_with_field_one_kwarg_unknown_value.py"),
            [
                {
                    "name": "bar",
                    "class_name": "Char",
                    "start_pos": (7, 10),
                    "end_pos": (9, 5),
                    "args": [],
                    "kwargs": [
                        {
                            "name": "baz",
                            "value": UNKNOWN,
                            "start_pos": (8, 8),
                            "end_pos": (8, 14),
                        }
                    ],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "simple_model_with_field_one_kwarg_multiline_string.py"),
            [
                {
                    "name": "bar",
                    "class_name": "Char",
                    "start_pos": (7, 10),
                    "end_pos": (10, 5),
                    "args": [],
                    "kwargs": [
                        {
                            "name": "string",
                            "value": "Very long string",
                            "start_pos": (8, 8),
                            "end_pos": (9, 23),
                        }
                    ],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "simple_model_one_field_direct_import.py"),
            [
                {
                    "name": "bar",
                    "class_name": "Char",
                    "start_pos": (8, 10),
                    "end_pos": (8, 16),
                    "args": [],
                    "kwargs": [],
                }
            ],
        ),
        ("simple_addon", ("models", "some_other_field_class.py"), []),
        ("simple_addon", ("models", "some_other_field_class_2.py"), []),
    ],
)
def test_field_definition_emitter(test_data_dir, addon_name, filename_parts, expected):
    manifest_path = ManifestPath(
        test_data_dir.joinpath(
            "field_definition_emitter", addon_name, "__manifest__.py"
        )
    )
    addon = Addon(manifest_path, parse_manifest(manifest_path), 12)
    addon_path = AddonPath(
        addon,
        test_data_dir.joinpath("field_definition_emitter", addon_name, *filename_parts),
    )

    python_emitter = PythonEmitter()
    model_emitter = ModelDefinitionEmitter()
    field_emitter = FieldDefinitionEmitter()

    fields = []
    for module in python_emitter.on_addon_path(addon_path):
        for model in model_emitter.on_python_module(module):
            fields.extend(field for field in field_emitter.on_model_definition(model))

    actual = [
        subdict(
            dataclasses.asdict(f),
            "name",
            "class_name",
            "args",
            "kwargs",
            "start_pos",
            "end_pos",
        )
        for f in fields
    ]
    assert expected == actual
