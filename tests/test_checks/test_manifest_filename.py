import yarl
from odin.addon import AddonPath
from odin.checks.addon import ManifestFilename
from odin.issue import Issue, Location
from odin.main import check_addon


def test_manifest_filename(test_data_dir):
    manifest_path = test_data_dir / "manifest_filename" / "__openerp__.py"
    issues = list(
        check_addon(manifest_path, {"manifest_filename": ManifestFilename}, version=10)
    )
    assert issues == [
        Issue(
            "deprecated_manifest_filename",
            'Starting with Odoo 10, addon manifest files should be named "__manifest__.py"',
            AddonPath(manifest_path),
            [Location(manifest_path)],
            categories=["deprecated"],
            sources=[
                yarl.URL(
                    "https://github.com/odoo/odoo/commit/4339196e5231aa734a0154e2f4e88b2e54f27d48"
                )
            ],
        )
    ]
