import dataclasses

import pytest

from odd.addon import Addon, ManifestPath, parse_manifest
from odd.check.path_emitter import AddonPath
from odd.check.python_emitter import ModelDefinitionEmitter, PythonEmitter

from ..common import subdict


@pytest.mark.parametrize(
    "addon_name, filename_parts, expected",
    [
        ("simple_addon", ("simple_class.py",), []),
        (
            "simple_addon",
            ("models", "simple_model.py"),
            [
                {
                    "class_name": "Foo",
                    "params": {"_name": "foo"},
                    "bases": [("models", "Model")],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "simple_abstract_model.py"),
            [
                {
                    "class_name": "BaseFoo",
                    "params": {"_name": "afoo"},
                    "bases": [("models", "AbstractModel")],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "simple_transient_model.py"),
            [
                {
                    "class_name": "FooWizard",
                    "params": {"_name": "foo.wizard"},
                    "bases": [("models", "TransientModel")],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "unknown_model_class.py"),
            [
                {
                    "class_name": "Foo",
                    "params": {"_name": "foo"},
                    "bases": [("models", "AwesomeModel")],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "model_multi_base_class.py"),
            [
                {
                    "class_name": "IrQWeb",
                    "params": {"_name": "ir.qweb"},
                    "bases": [("models", "AbstractModel"), ("QWeb",)],
                }
            ],
        ),
        (
            "simple_addon",
            ("models", "full_import_path.py"),
            [
                {
                    "class_name": "Foo",
                    "params": {"_name": "foo"},
                    "bases": [("odoo", "models", "Model")],
                }
            ],
        ),
    ],
)
def test_model_definition_emitter(test_data_dir, addon_name, filename_parts, expected):
    manifest_path = ManifestPath(
        test_data_dir.joinpath(
            "model_definition_emitter", addon_name, "__manifest__.py"
        )
    )
    addon = Addon(manifest_path, parse_manifest(manifest_path), 12)
    addon_path = AddonPath(
        addon,
        test_data_dir.joinpath("model_definition_emitter", addon_name, *filename_parts),
    )

    python_emitter = PythonEmitter()
    model_emitter = ModelDefinitionEmitter()

    models = []
    for module in python_emitter.on_addon_path(addon_path):
        models.extend(model_emitter.on_python_module(module))

    actual = [
        subdict(dataclasses.asdict(m), "class_name", "params", "bases") for m in models
    ]
    assert expected == actual
