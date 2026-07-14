"""HTML sanitization for user-authored rich text (article bodies).

Article content is stored as HTML produced by the rich-text editor and later rendered
verbatim in the browser. Sanitizing at write time — at the API boundary — ensures the
stored value is safe no matter which client renders it, closing the stored-XSS vector
that unsanitized ``dangerouslySetInnerHTML`` would otherwise expose.
"""
import bleach

# Formatting tags the editor can legitimately emit. Anything else (script, iframe,
# style, form, object, embed, ...) is stripped.
ALLOWED_TAGS = [
    "p", "br", "hr", "span", "div",
    "strong", "b", "em", "i", "u", "s", "strike", "del", "mark", "sub", "sup",
    "blockquote", "code", "pre",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
]

# Only these attributes survive per tag; event handlers (onclick, onerror, ...) and
# style are never in the list, so they are always removed.
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "span": ["class"],
    "code": ["class"],
    "pre": ["class"],
    "div": ["class"],
    "th": ["colspan", "rowspan", "scope"],
    "td": ["colspan", "rowspan"],
}

# Disallow javascript:/vbscript:/data: URLs. Relative URLs (e.g. "/media/x.png") carry
# no protocol and are permitted by bleach.
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(html: str) -> str:
    """Return a sanitized copy of ``html`` safe to render as-is in a browser."""
    if not html:
        return html
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
