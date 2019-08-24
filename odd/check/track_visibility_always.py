from odd.check import Check
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1, get_string_node_value, is_string_node, walk
from odd.utils import odoo_commit_url


class TrackVisibilityAlways(Check):
    _handles = {"python_module"}

    def on_python_module(self, python_module):
        if python_module.addon.version < 12:
            return

        for node in walk(python_module.module):
            if node.type != "argument":
                continue
            if (
                node.children[0].type == "name"
                and node.children[0].value == "track_visibility"
                and node.children[1].type == "operator"
                and node.children[1].value == "="
                and is_string_node(node.children[2])
                and get_string_node_value(node.children[2]) == "always"
            ):
                yield Issue(
                    "track_visibility_always_deprecated",
                    'Field `track_visibility` attribute value "always" is '
                    "deprecated since version 12.0",
                    python_module.addon.manifest_path,
                    [Location(python_module.path, [column_index_1(node.start_pos)])],
                    categories=["deprecated"],
                    sources=[
                        odoo_commit_url("c99de4551583e801ecc6669ac456c4f7e2eef1da")
                    ],
                )
