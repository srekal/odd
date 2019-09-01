from odd.check import Check
from odd.check.python_emitter import FieldDefinition
from odd.issue import Issue, Location
from odd.parso_utils import column_index_1
from odd.utils import odoo_commit_url


class TrackVisibilityAlways(Check):
    _handles = {"field_definition"}

    def on_field_definition(self, field: FieldDefinition):
        addon = field.model.addon
        if addon.version < 12:
            return

        for kwarg in field.kwargs:
            if kwarg.name == "track_visibility" and kwarg.value == "always":
                yield Issue(
                    "track_visibility_always_deprecated",
                    'Field `track_visibility` attribute value "always" is '
                    "deprecated since version 12.0",
                    addon.manifest_path,
                    [Location(field.model.path, [column_index_1(kwarg.start_pos)])],
                    categories=["deprecated"],
                    sources=[
                        odoo_commit_url("c99de4551583e801ecc6669ac456c4f7e2eef1da")
                    ],
                )
