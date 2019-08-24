import pytest
from odd.check.csv_row_emitter import CSVRow
from odd.check.addon_file_emitter import DataFile
from odd.addon import Addon, ManifestPath, parse_manifest
from odd.check.csv_row_emitter import CSVRowEmitter


@pytest.mark.parametrize(
    "addon_name, filename_parts, expected",
    [
        (
            "simple_addon",
            ("foo.csv",),
            [({"id": "a", "foo": "bar"}, 2), ({"id": "b", "foo": "baz"}, 3)],
        )
    ],
)
def test_csv_row_emitter(test_data_dir, addon_name, filename_parts, expected):
    manifest_path = ManifestPath(
        test_data_dir.joinpath("csv_row_emitter", addon_name, "__manifest__.py")
    )
    addon = Addon(manifest_path, parse_manifest(manifest_path), 12)
    data_file_path = test_data_dir.joinpath(
        "csv_row_emitter", addon_name, *filename_parts
    )
    data_file = DataFile(addon, data_file_path)
    emitter = CSVRowEmitter()
    actual = list(emitter.on_data_file(data_file))
    expected = [
        CSVRow(addon, data_file_path, row, line_no) for row, line_no in expected
    ]
    assert expected == actual
