import pathlib

import pytest

from odin.addon import AddonPath
from odin.issue import Issue, Location
from odin.utils import format_issue, lookup_version_list

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
        (
            Issue(
                "foo", "bar", TEST_ADDON_PATH, [Location(TEST_MANIFEST_PATH, [(2, 10)])]
            ),
            "baz (__manifest__.py, line: 2, column: 10): bar",
        ),
    ],
)
def test_format_issue(issue, expected):
    actual = format_issue(issue)
    assert actual == expected


@pytest.mark.parametrize(
    "version_map, version, expected",
    [
        ({"==8": ["a"]}, 8, ["a"]),
        ({"==8": ["a"]}, 9, []),
        ({"==8": ["a"], "<10": ["b"]}, 9, ["b"]),
        ({"==8": ["a"]}, 7, ValueError(r"^Unsupported version")),
        ({"==8": ["a"]}, "10", TypeError(r"^Invalid version")),
        ({"~8": ["a"]}, 8, ValueError(r"^Invalid version specification")),
    ],
)
def test_lookup_version_list(version_map, version, expected):
    if isinstance(expected, Exception):
        with pytest.raises(type(expected), match=expected.args[0]):
            lookup_version_list(version_map, version)
    else:
        actual = lookup_version_list(version_map, version)
        assert expected == actual
