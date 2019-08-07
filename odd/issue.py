import dataclasses
import pathlib
import typing

from odd.addon import AddonPath


@dataclasses.dataclass
class Location:
    path: pathlib.Path
    line_numbers: typing.List[
        typing.Union[int, typing.Tuple[int, int]]
    ] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Issue:
    slug: str
    description: str
    addon_path: AddonPath
    locations: typing.List[Location] = dataclasses.field(default_factory=list)
    categories: typing.List[str] = dataclasses.field(default_factory=list)
    sources: typing.List[str] = dataclasses.field(default_factory=list)