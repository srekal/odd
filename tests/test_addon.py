import pytest
from odd.addon import Addon, ManifestPath, discover_addons, parse_manifest


@pytest.mark.parametrize(
    "addon_name, expected",
    [
        ("addon_qweb", ["a.xml", "b.xml", "c.xml"]),
        ("addon_qweb_glob", ["a.xml", "b.xml"]),
    ],
)
def test_qweb_glob(test_data_dir, addon_name, expected):
    addon_dir = test_data_dir / "addon" / addon_name
    manifest_path = ManifestPath(addon_dir / "__manifest__.py")
    addon = Addon(manifest_path, parse_manifest(manifest_path), version=12)
    qweb_xml_path = addon_dir / "static" / "src" / "xml"
    assert sorted(addon.qweb_files) == sorted(qweb_xml_path / p for p in expected)


@pytest.mark.parametrize(
    "directory, expected",
    [
        ("single", [("manifest", "__manifest__.py"), ("openerp", "__openerp__.py")]),
        (
            "nested",
            [("a", "manifest", "__manifest__.py"), ("b", "openerp", "__openerp__.py")],
        ),
    ],
)
def test_discover_addons(test_data_dir, directory, expected):
    actual = sorted(
        mp.path for mp in discover_addons(test_data_dir / "discover_addons" / directory)
    )
    expected = [
        test_data_dir.joinpath("discover_addons", directory, *a) for a in expected
    ]
    assert actual == expected
