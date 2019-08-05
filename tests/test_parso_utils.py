import pytest
import parso

from odin.parso_utils import get_model_definition, Model, Field, FieldKwarg, UNKNOWN


@pytest.mark.parametrize(
    "python_module, extract_fields, expected",
    [
        ("simple_class.py", True, None),
        ("simple_model.py", True, Model("foo", "Foo", bases=[("models", "Model")])),
        (
            "simple_model_with_field.py",
            True,
            Model(
                "foo",
                "Foo",
                bases=[("models", "Model")],
                fields=[Field("bar", "Char", (8, 10), (8, 23))],
            ),
        ),
        (
            "simple_model_with_field.py",
            False,
            Model("foo", "Foo", bases=[("models", "Model")]),
        ),
        (
            "simple_model_one_field_direct_import.py",
            True,
            Model(
                "foo",
                "Foo",
                bases=[("models", "Model")],
                fields=[Field("bar", "Char", (9, 10), (9, 16))],
            ),
        ),
        (
            "full_import_path.py",
            True,
            Model(
                "foo",
                "Foo",
                bases=[("odoo", "models", "Model")],
                fields=[Field("bar", "Char", (8, 10), (8, 28))],
            ),
        ),
        (
            "some_other_field_class.py",
            True,
            Model("foo", "Foo", bases=[("models", "Model")]),
        ),
        (
            "some_other_field_class_2.py",
            True,
            Model("foo", "Foo", bases=[("models", "Model")]),
        ),
        (
            "simple_model_with_field_one_kwarg.py",
            True,
            Model(
                "foo",
                "Foo",
                bases=[("models", "Model")],
                fields=[
                    Field(
                        "bar",
                        "Char",
                        (8, 10),
                        (10, 5),
                        kwargs=[
                            FieldKwarg(
                                "string", "Bar", start_pos=(9, 8), end_pos=(9, 20)
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
                "foo",
                "Foo",
                bases=[("models", "Model")],
                fields=[
                    Field(
                        "bar",
                        "Char",
                        (8, 10),
                        (10, 5),
                        kwargs=[
                            FieldKwarg(
                                "baz", UNKNOWN, start_pos=(9, 8), end_pos=(9, 14)
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
                "foo",
                "Foo",
                bases=[("models", "Model")],
                fields=[
                    Field(
                        "bar",
                        "Char",
                        (8, 10),
                        (11, 5),
                        kwargs=[
                            FieldKwarg(
                                "string",
                                "Very long string",
                                start_pos=(9, 8),
                                end_pos=(10, 23),
                            )
                        ],
                    )
                ],
            ),
        ),
        (
            "simple_abstract_model.py",
            True,
            Model("afoo", "BaseFoo", bases=[("models", "AbstractModel")]),
        ),
        (
            "simple_transient_model.py",
            True,
            Model("foo.wizard", "FooWizard", bases=[("models", "TransientModel")]),
        ),
        (
            "unknown_model_class.py",
            True,
            Model("foo", "Foo", bases=[("models", "AwesomeModel")]),
        ),
        ("django_fields.py", True, Model("foo", "Foo", bases=[("models", "Model")])),
        (
            "django_fields_2.py",
            True,
            Model("foo", "Foo", bases=[("django", "db", "models", "Model")]),
        ),
        (
            "model_multi_base_class.py",
            True,
            Model("ir.qweb", "IrQWeb", bases=[("models", "AbstractModel"), ("QWeb",)]),
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
