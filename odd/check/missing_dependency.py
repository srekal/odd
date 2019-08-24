import contextlib
import importlib.resources
import logging
import sqlite3
import typing

from odd.addon import Addon
from odd.check import Check
from odd.const import UNKNOWN
from odd.db_utils import get_db_conn
from odd.issue import Issue


_LOG = logging.getLogger(__name__)


def get_transitive_dependencies(
    cr: sqlite3.Cursor, addon: Addon
) -> typing.Optional[typing.Set[str]]:
    dependencies = set(addon.manifest.get("depends") or []) or {"base"}
    to_expand = dependencies.copy()
    while to_expand:
        dependency_name = to_expand.pop()

        cr.execute(
            """
SELECT id
  FROM addon
 WHERE name = :name
   AND odoo_version = :odoo_version
;""",
            {"name": dependency_name, "odoo_version": addon.version},
        )

        addon_ids = cr.fetchone()
        if addon_ids:
            addon_id = addon_ids[0]
        else:
            _LOG.debug(
                'Addon "%s" not found in addon database, '
                "stoping further dependency tree expansion",
                dependency_name,
            )
            return None

        cr.execute(
            """
SELECT addon.name
FROM addon
LEFT JOIN dependency
ON dependency.dependency_id = addon.id
WHERE dependency.addon_id = :addon_id
        ;""",
            {"addon_id": addon_id},
        )
        dependency_names = {d[0] for d in cr.fetchall()}
        to_expand.update(d for d in dependency_names if d not in dependencies)
        dependencies.update(dependency_names)

    return dependencies


class MissingDependency(Check):
    _handles = {"external_id_reference"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._external_ids = []

    def on_external_id_reference(self, ref):
        self._external_ids.append(ref)
        yield from ()

    def on_after(self, addon):
        with importlib.resources.path("odd.data", "addon_db.sqlite") as db_path:
            with contextlib.closing(get_db_conn(db_path)) as conn, conn as conn:
                all_dependencies = get_transitive_dependencies(conn.cursor(), addon)

        if all_dependencies is None:
            return

        for ext_id in self._external_ids:
            if (
                ext_id.addon_name is None
                or ext_id.addon_name == addon.name
                or ext_id.addon_name is UNKNOWN
            ):
                continue

            if ext_id.addon_name not in all_dependencies:
                yield Issue(
                    "missing_dependency",
                    f'Addon references other addon "{ext_id.addon_name}", '
                    f"but it is not in the transitive dependency tree",
                    addon.manifest_path,
                    locations=[ext_id.location],
                    categories=["correctness"],
                )
