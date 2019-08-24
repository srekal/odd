import abc
import typing


class Check(abc.ABC):
    _emits: typing.Set[str] = set()
    _handles: typing.Set[str] = set()
