import abc
import pathlib

import parso

from odd.addon import Addon


class AddonCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, addon: Addon):
        """Actual plugin"""


class PathCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, addon: Addon, path: pathlib.Path):
        """Receives paths (files or directories)."""


class PythonCheck(abc.ABC):
    @abc.abstractmethod
    def check(
        self, addon: Addon, filename: pathlib.Path, module: parso.python.tree.Module
    ):
        """Actual plugin"""


class XMLCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, addon: Addon, filename: pathlib.Path, tree):
        """Actual plugin"""
