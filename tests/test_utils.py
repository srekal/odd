import pathlib

import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.utils import format_issue

TEST_MANIFEST_PATH = pathlib.Path("/addons/baz/__manifest__.py")
TEST_ADDON_PATH = AddonPath(TEST_MANIFEST_PATH)


@pytest.mark.parametrize(
    "issue, expected",
    [
        (Issue("foo", "bar", TEST_ADDON_PATH), "baz: bar"),
        (
            Issue("foo", "bar", TEST_ADDON_PATH, [Location(TEST_MANIFEST_PATH, [5])]),
            "baz (__manifest__.py, line: 5): bar",
        ),
        (
            Issue(
                "foo", "bar", TEST_ADDON_PATH, [Location(TEST_MANIFEST_PATH, [2, 10])]
            ),
            "baz (__manifest__.py, lines: 2, 10): bar",
        ),
    ],
)
def test_format_issue(issue, expected):
    actual = format_issue(issue)
    assert actual == expected
