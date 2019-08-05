import pytest
import parso

from odin.parso_utils import get_model_definition, Model, Field, FieldKwarg, UNKNOWN


@pytest.mark.parametrize(
    "python_module, extract_fields, expected",
    [
        ("simple_class.py", True, Model("MyClass")),
        (
            "simple_model.py",
            True,
            Model("Foo", params={"_name": "foo"}, bases=[("models", "Model")]),
        ),
        (
            "simple_model_with_field.py",
            True,
            Model(
                "Foo",
                params={"_name": "foo"},
                bases=[("models", "Model")],
                fields=[Field("bar", "Char", (7, 10), (7, 23))],
            ),
        ),
        (
            "simple_model_with_field.py",
            False,
            Model("Foo", params={"_name": "foo"}, bases=[("models", "Model")]),
        ),
        (
            "simple_model_one_field_direct_import.py",
            True,
            Model(
                "Foo",
                params={"_name": "foo"},
                bases=[("models", "Model")],
                fields=[Field("bar", "Char", (8, 10), (8, 16))],
            ),
        ),
        (
            "full_import_path.py",
            True,
            Model(
                "Foo",
                params={"_name": "foo"},
                bases=[("odoo", "models", "Model")],
                fields=[Field("bar", "Char", (7, 10), (7, 28))],
            ),
        ),
        (
            "some_other_field_class.py",
            True,
            Model("Foo", params={"_name": "foo"}, bases=[("models", "Model")]),
        ),
        (
            "some_other_field_class_2.py",
            True,
            Model("Foo", params={"_name": "foo"}, bases=[("models", "Model")]),
        ),
        (
            "simple_model_with_field_one_kwarg.py",
            True,
            Model(
                "Foo",
                params={"_name": "foo"},
                bases=[("models", "Model")],
                fields=[
                    Field(
                        "bar",
                        "Char",
                        (7, 10),
                        (9, 5),
                        kwargs=[
                            FieldKwarg(
                                "string", "Bar", start_pos=(8, 8), end_pos=(8, 20)
                            )
                        ],
                    )
                ],
            ),
        ),
        (
            "simple_model_with_field_one_kwarg_unknown_value.py",
            True,
            Model(
                "Foo",
                params={"_name": "foo"},
                bases=[("models", "Model")],
                fields=[
                    Field(
                        "bar",
                        "Char",
                        (7, 10),
                        (9, 5),
                        kwargs=[
                            FieldKwarg(
                                "baz", UNKNOWN, start_pos=(8, 8), end_pos=(8, 14)
                            )
                        ],
                    )
                ],
            ),
        ),
        (
            "simple_model_with_field_one_kwarg_multiline_string.py",
            True,
            Model(
                "Foo",
                params={"_name": "foo"},
                bases=[("models", "Model")],
                fields=[
                    Field(
                        "bar",
                        "Char",
                        (7, 10),
                        (10, 5),
                        kwargs=[
                            FieldKwarg(
                                "string",
                                "Very long string",
                                start_pos=(8, 8),
                                end_pos=(9, 23),
                            )
                        ],
                    )
                ],
            ),
        ),
        (
            "simple_abstract_model.py",
            True,
            Model(
                "BaseFoo", params={"_name": "afoo"}, bases=[("models", "AbstractModel")]
            ),
        ),
        (
            "simple_transient_model.py",
            True,
            Model(
                "FooWizard",
                params={"_name": "foo.wizard"},
                bases=[("models", "TransientModel")],
            ),
        ),
        (
            "unknown_model_class.py",
            True,
            Model("Foo", params={"_name": "foo"}, bases=[("models", "AwesomeModel")]),
        ),
        (
            "django_fields.py",
            True,
            Model("Foo", params={"_name": "foo"}, bases=[("models", "Model")]),
        ),
        (
            "django_fields_2.py",
            True,
            Model(
                "Foo",
                params={"_name": "foo"},
                bases=[("django", "db", "models", "Model")],
            ),
        ),
        (
            "model_multi_base_class.py",
            True,
            Model(
                "IrQWeb",
                params={"_name": "ir.qweb"},
                bases=[("models", "AbstractModel"), ("QWeb",)],
            ),
        ),
    ],
)
def test_get_model_definition(test_data_dir, python_module, extract_fields, expected):
    with (test_data_dir / "parso_utils" / python_module).open(mode="rb") as f:
        module = parso.parse(f.read())

    class_defs = list(module.iter_classdefs())
    assert len(class_defs) == 1
    actual = get_model_definition(class_defs[0], extract_fields=extract_fields)
    assert expected == actual
