import ast

from odin.checks import FileCheck
from odin.issue import Issue, Location
from odin.utils import odoo_commit_url


class TrackVisibilityAlways(FileCheck):
    def check(self, filename, addon):
        if addon.version < 12 or filename.suffix.lower() != ".py":
            return

        with filename.open(mode="rb") as f:
            tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if not isinstance(node, ast.keyword):
                    continue
                if (
                    node.arg == "track_visibility"
                    and isinstance(node.value, ast.Str)
                    and node.value.s == "always"
                ):
                    yield Issue(
                        "track_visibility_always_deprecated",
                        'Field `track_visibility` attribute value "always" is deprecated since version 12.0',
                        addon.addon_path,
                        [Location(filename, [node.value.lineno])],
                        categories=["deprecated"],
                        sources=[
                            odoo_commit_url("c99de4551583e801ecc6669ac456c4f7e2eef1da")
                        ],
                    )
