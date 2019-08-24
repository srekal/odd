import dataclasses


@dataclasses.dataclass
class Artifact:
    """Base class of a result which can be returned by a :class:`Check`."""
