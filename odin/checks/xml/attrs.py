from odin.checks import XMLCheck
from odin.const import SUPPORTED_VERSIONS
from odin.issue import Issue, Location
from odin.xmlutils import get_model_records, get_root, get_view_arch
from odin.utils import expand_version_list

GLOBAL_ATTRS = {
    "accesskey",
    "autocapitalize",
    "class",
    "contenteditable",
    "contextmenu",
    # "data-*"
    "dir",
    "draggable",
    "dropzone",
    "hidden",
    "id",
    "inputmode",
    "is",
    "itemid",
    "itemprop",
    "itemref",
    "itemscope",
    "itemtype",
    "lang",
    "slot",
    "spellcheck",
    "style",
    "tabindex",
    "title",
    "translate",
}
SEMANTIC_ELEMENTS = {
    "article",
    "aside",
    "details",
    "figcaption",
    "figure",
    "footer",
    "header",
    "main",
    "mark",
    "nav",
    "section",
    "summary",
    "time",
}
HTML_ELEMENTS = {
    "a",
    "abbr",
    "address",
    "area",
    "base",
    "bdi",
    "bdo",
    "button",
    "caption",
    "p",
    "div",
    "span",
    "table",
    "tr",
    "td",
    "th",
    "thead",
    "tbody",
    "tfoot",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "input",
    "label",
    "form",
    "ul",
    "ol",
    "li",
    "option",
    "strong",
    "em",
    "select",
    "textarea",
    "nav",
    "title",
    "script",
    "link",
    "iframe",
    "hr",
    "style",
    "audio",
    "video",
    "source",
    "col",
    "body",
    "small",
    "meta",
    "sup",
    "sub",
    "noscript",
    "blockquote",
    "del",
    "cite",
    "dd",
    "dl",
    "dt",
    "em",
    "br",
    "canvas",
    "colgroup",
    "b",
    "i",
    "u",
    "s",
    "html",
    "head",
    "code",
    "pre",
    "svg",
    "wbr",
    "template",
    "picture",
    *SEMANTIC_ELEMENTS,
}
DEPRECATED_HTML_ELEMENTS = {
    "acronym",
    "applet",
    "basefont",
    "bgsound",
    "big",
    "blink",
    "font",
    "strike",
}
ODOO_ELEMENTS = {"xpath", "t", "attribute"}


ODOO_ATTRS = {"position", "groups"}

ODOO_ELEMENT_ATTR_VERSION_MAP = {
    "xpath": {">=8": {"expr", "position"}},
    "attribute": {">=8": {"name"}, ">=9": {"add", "remove", "separator"}},
    "t": {
        ">=8": {
            "t-if",
            "t-foreach",
            "t-as",
            "t-set",
            "t-value",
            "t-valuef",
            "t-call",
            "t-esc",
            "t-esc-options",
            "t-raw",
            "t-lang",
            "t-debug",
            "t-call-assets",
            "t-js",
            "t-css",
            "t-ignore",
            "t-placeholder",
            "t-translation",
            # Extension
            "position",
        },
        ">=9": {"t-snippet", "t-thumbnail"},
        ">=10": {"t-else", "t-elif", "t-options"},
        ">=11": {"t-install"},
    },
}
ODOO_ELEMENT_ATTRS = {
    tag: expand_version_list(version_map, *SUPPORTED_VERSIONS, result_cls=set)
    for tag, version_map in ODOO_ELEMENT_ATTR_VERSION_MAP.items()
}

KNOWN_ATTRS = {
    "svg": {"height", "preserveAspectRatio", "viewBox", "width", "x", "y"},
    "source": {"src", "srcset", "media", "sizes", "type"},
    "html": {"xmlns"},
    "colgroup": {"span"},
    "del": {"cite", "datetime"},
    "blockquote": {"cite"},
    "ol": {"reversed", "start", "type"},
    "time": {"datetime"},
    "meta": {"charset", "content", "http-equiv", "name"},
    "col": {"span"},
    "style": {"media", "type"},
    "iframe": {
        "allow",
        "allowfullscreen",  # legacy, redefined as allow="fullscreen"
        "allowpaymentrequest",  # legacy, redefined as allow="payment"
        "csp",
        "height",
        "importance",
        "name",
        "referrerpolicy",
        "sandbox",
        "src",
        "srcdoc",
        "width",
    },
    "textarea": {
        "autofocus",
        "cols",
        "dirname",
        "disabled",
        "form",
        "maxlength",
        "minlength",
        "name",
        "placeholder",
        "readonly",
        "required",
        "rows",
        "spellcheck",
        "wrap",
    },
    "img": {
        "alt",
        "crossorigin",
        "height",
        "ismap",
        "longdesc",
        "sizes",
        "src",
        "srcset",
        "usemap",
        "width",
    },
    "select": {"autofocus", "disabled", "form", "multiple", "name", "required", "size"},
    "option": {"disabled", "label", "selected", "value"},
    "button": {
        "autofocus",
        "disabled",
        "form",
        "formaction",
        "formenctype",
        "formmethod",
        "formnovalidate",
        "formtarget",
        "name",
        "type",
        "value",
    },
    "form": {
        "accept-charset",
        "action",
        "autocomplete",
        "enctype",
        "method",
        "name",
        "novalidate",
        "target",
    },
    "a": {
        "download",
        "href",
        "hreflang",
        "media",
        "ping",
        "referrerpolicy",
        "rel",
        "target",
        "type",
    },
    "area": {
        "alt",
        "coords",
        "download",
        "href",
        "hreflang",
        "ping",
        "referrerpolicy",
        "rel",
        "shape",
        "target",
    },
    "audio": {"autoplay", "controls", "crossorigin", "loop", "muted", "preload", "src"},
    "base": {"href", "target"},
    "bdo": {"dir"},
    "caption": {"align"},
    "script": {
        "async",
        "charset",
        "defer",
        "integrity",
        "nomodule",
        "nonce",
        "referrerpolicy",
        "src",
        "type",
    },
    "link": {
        "as",
        "crossorigin",
        "disabled",
        "href",
        "hreflang",
        "importance",
        "integrity",
        "media",
        "rel",
        "sizes",
        "type",
    },
    "td": {"colspan", "headers", "rowspan"},
    "th": {"abbr", "colspan", "headers", "rowspan", "scope", "sorted"},
    "label": {"for", "form"},
    "input": {
        "accept",
        "align",
        "alt",
        "autocomplete",
        "autofocus",
        "checked",
        "dirname",
        "disabled",
        "form",
        "formaction",
        "formenctype",
        "formmethod",
        "formnovalidate",
        "formtarget",
        "height",
        "list",
        "max",
        "maxlength",
        "min",
        "multiple",
        "name",
        "pattern",
        "placeholder",
        "readonly",
        "required",
        "size",
        "src",
        "step",
        "type",
        "value",
        "width",
    },
}
DEPRECATED_ATTRIBUTES = {
    "svg": {"baseProfile", "contentScriptType", "contentStyleType", "version"},
    "pre": {"width"},
    "head": {"profile"},
    "colgroup": {"align", "char", "charoff", "valign", "width"},
    "body": {"alink", "background", "bgcolor", "link", "text", "vlink"},
    "img": {"align", "border", "hspace", "vspace"},
    "a": {"charset", "coords", "name", "rev", "shape"},
    "area": {"accesskey", "name", "nohref", "tabindex", "type"},
    "table": {
        "align",
        "bgcolor",
        "border",
        "cellpadding",
        "cellspacing",
        "frame",
        "rules",
        "summary",
        "width",
    },
    "td": {
        "abbr",
        "align",
        "axis",
        "bgcolor",
        "char",
        "charoff",
        "height",
        "nowrap",
        "scope",
        "valign",
        "width",
    },
    "ol": {"compact"},
    "col": {"align", "char", "charoff", "valign", "width"},
    "iframe": {
        "align",
        "frameborder",
        "longdesc",
        "marginheight",
        "marginwidth",
        "scrolling",
    },
}

"""
print(",".join(sorted(HTML_ELEMENTS)))
HTML_ELEMENTS = frozenset(
    "a,abbr,address,article,aside,audio,b,button,col,div,em,form,h2,h3,h4,h5,h6,header,hr,i,iframe,img,input,label,li,link,meta,nav,ol,option,p,script,section,select,small,span,strong,style,sup,table,tbody,td,textarea,tfooth1,th,thead,title,tr,ul".split(","))
for k in sorted(KNOWN_ATTRS):
    print("%s;%s" % (k, ",".join(sorted(KNOWN_ATTRS[k]))))
"""
TEXT_ELEMENTS = {
    "p",
    "span",
    "div",
    "a",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "strong",
    "em",
    "small",
    "td",
    "th",
    "address",
    "label",
    "title",
    "option",
    "sup",
    "sub",
    "b",
    "i",
    "u",
    "s",
    "del",
    "dt",
    "dd",
}

ARIA_ATTRS = {
    "role",
    "aria-hidden",
    "aria-label",
    "aria-labelledby",
    "aria-expanded",
    "aria-valuenow",
    "aria-valuemin",
    "aria-valuemax",
    "aria-controls",
    "aria-colspan",
    "aria-current",
    "aria-selected",
    "aria-haspopup",
    "aria-disabled",
}

HTML_ELEMENT_T_ATTRS_VERSION_MAP = {
    "t-if": {">=8": HTML_ELEMENTS},
    "t-elif": {">=10": HTML_ELEMENTS},
    "t-else": {">=10": HTML_ELEMENTS},
    "t-field": {">=8": TEXT_ELEMENTS},
    "t-raw": {">=8": {"p", "span"}},
    "t-esc": {">=8": TEXT_ELEMENTS},
    "t-foreach": {
        ">=8": {
            "div",
            "tr",
            "th",
            "td",
            "option",
            "ul",
            "ol",
            "li",
            "span",
            "p",
            "section",
            "label",
            "dl",
        }
    },
    "t-as": {
        ">=8": {
            "div",
            "tr",
            "th",
            "td",
            "option",
            "ul",
            "ol",
            "li",
            "span",
            "p",
            "section",
            "label",
        }
    },
    "t-options": {">=10": {"div", "h1", "h2", "h3", "h4", "h5", "h6", "b"}},
    "t-ignore": {">=8": HTML_ELEMENTS},
}
HTML_ELEMENT_T_ATTRS = {}
for attr, version_map in HTML_ELEMENT_T_ATTRS_VERSION_MAP.items():
    HTML_ELEMENT_T_ATTRS[attr] = expand_version_list(
        version_map, *SUPPORTED_VERSIONS, result_cls=set
    )


class Attrs(XMLCheck):
    def check(self, addon, filename, tree):
        if filename not in addon.data_files and filename not in addon.demo_files:
            return
        for template in tree.xpath("//template"):
            for el in template.xpath(".//*"):
                tag = el.tag.lower()

                if tag not in HTML_ELEMENTS and tag not in ODOO_ELEMENTS:
                    if tag in DEPRECATED_HTML_ELEMENTS:
                        yield Issue(
                            "deprecated_html_element",
                            f"Deprecated HTML element `<{el.tag}>`",
                            addon.addon_path,
                            [Location(filename, [el.sourceline])],
                            categories=["deprecated", "correctness"],
                        )
                    elif el.getparent().tag.lower() == "svg":
                        pass
                    else:
                        yield Issue(
                            "unknown_html_element",
                            f"Unknown HTML element `<{el.tag}>`",
                            addon.addon_path,
                            [Location(filename, [el.sourceline])],
                            categories=["correctness"],
                        )
                    continue

                allowed_attrs = set()
                if tag in HTML_ELEMENTS:
                    allowed_attrs.update(GLOBAL_ATTRS)
                    allowed_attrs.update(ARIA_ATTRS)
                allowed_attrs.update(KNOWN_ATTRS.get(el.tag, set()))

                unknown_attrs = set()
                for attr in el.attrib:
                    if attr == "t-field":
                        if tag == "t":
                            yield Issue(
                                "t_field_on_t",
                                "t-field can not be used on a t element, provide an actual HTML node",
                                addon.addon_path,
                                [Location(filename, [el.sourceline])],
                                categories=["correctness"],
                            )

                        if tag in {
                            "table",
                            "tbody",
                            "thead",
                            "tfoot",
                            "tr",
                            "td",
                            "li",
                            "ul",
                            "ol",
                            "dl",
                            "dt",
                            "dd",
                        }:
                            yield Issue(
                                "t_field_unsupported",
                                f"RTE widgets do not work correctly on {tag} elements",
                                addon.addon_path,
                                [Location(filename, [el.sourceline])],
                                categories=["correctness"],
                            )

                    if attr in DEPRECATED_ATTRIBUTES.get(tag, set()):
                        yield Issue(
                            "deprecated_html_attribute",
                            f"`<{tag}>` element attribute `{attr}` is deprecated",
                            addon.addon_path,
                            [Location(filename, [el.sourceline])],
                            categories=["deprecated"],
                        )
                        continue

                    if attr.startswith("data-"):
                        continue
                    if attr.startswith("t-att-"):
                        attr_name = attr[len("t-att-") :]
                        if attr_name in allowed_attrs:
                            continue
                    if attr.startswith("t-attf-"):
                        if attr[len("t-attf-") :] in allowed_attrs:
                            continue
                    if attr.startswith("t-att-data-"):
                        continue
                    if attr.startswith("t-attf-data-"):
                        continue
                    if attr.startswith("t-as-") and "t-foreach" in el.attrib:
                        continue

                    if tag in ODOO_ELEMENT_ATTRS:
                        known_odoo_element_attrs = ODOO_ELEMENT_ATTRS[tag].get(
                            addon.version, set()
                        )
                        # Extra `t-` attribute for snippets.
                        if addon.version >= 11 and "t-thumbnail" in el.attrib:
                            known_odoo_element_attrs.add("string")
                        if attr in known_odoo_element_attrs:
                            continue

                    if attr in ODOO_ATTRS:
                        continue
                    if (
                        attr in HTML_ELEMENT_T_ATTRS
                        and tag in HTML_ELEMENT_T_ATTRS[attr][addon.version]
                    ):
                        continue
                    if attr not in allowed_attrs:
                        unknown_attrs.add(attr)

                for unknown_attr in unknown_attrs:
                    yield Issue(
                        "unknown_attribute",
                        f"`<{el.tag}>` has an unknown attribute `{unknown_attr}`",
                        addon.addon_path,
                        [Location(filename, [el.sourceline])],
                        categories=["correctness"],
                    )
