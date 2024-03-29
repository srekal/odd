import collections

MANIFEST_FILENAMES = frozenset(("__manifest__.py", "__openerp__.py"))

MIN_SUPPORTED_VERSION = 8
MAX_SUPPORTED_VERSION = 13
SUPPORTED_VERSIONS = range(MIN_SUPPORTED_VERSION, MAX_SUPPORTED_VERSION + 1)
UNKNOWN = collections.namedtuple("Unknown", [])
