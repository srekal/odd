import typing

import lxml.etree as etree  # nosec


OdooVersion = int
Element = etree._Element
ElementGenerator = typing.Generator[Element, None, None]
