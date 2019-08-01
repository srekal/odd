import abc
import pathlib

import parso

from odin.addon import Addon


class AddonCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, addon: Addon):
        """Actual plugin"""


class FileCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, addon: Addon, filename: pathlib.Path):
        """Actual plugin"""


class PythonCheck(abc.ABC):
    @abc.abstractmethod
    def check(
        self, addon: Addon, filename: pathlib.Path, module: parso.tree.NodeOrLeaf
    ):
        """Actual plugin"""


class XMLCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, filename: pathlib.Path, tree, addon: Addon):
        """Actual plugin"""
