import pytest

from odin.main import get_checks


def test_get_checks_unknown_check_raises_error():
    with pytest.raises(KeyError, match=r"foobar"):
        get_checks({"foobar"})
