from odin.checks import PythonCheck
from odin.issue import Issue, Location
from odin.utils import odoo_commit_url, walk, get_string_node_value


class TrackVisibilityAlways(PythonCheck):
    def check(self, addon, filename, module):
        if addon.version < 12:
            return

        for node in walk(module):
            if node.type != "argument":
                continue
            if (
                node.children[0].type == "name"
                and node.children[0].value == "track_visibility"
                and node.children[1].type == "operator"
                and node.children[1].value == "="
                and node.children[2].type == "string"
                and get_string_node_value(node.children[2]) == "always"
            ):
                yield Issue(
                    "track_visibility_always_deprecated",
                    'Field `track_visibility` attribute value "always" is deprecated since version 12.0',
                    addon.addon_path,
                    [Location(filename, [node.start_pos])],
                    categories=["deprecated"],
                    sources=[
                        odoo_commit_url("c99de4551583e801ecc6669ac456c4f7e2eef1da")
                    ],
                )
