import abc
import pathlib

from odin.addon import Addon


class AddonCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, addon: Addon):
        """Actual plugin"""


class FileCheck(abc.ABC):
    @abc.abstractmethod
    def check(self, filename: pathlib.Path, addon: Addon):
        """Actual plugin"""
