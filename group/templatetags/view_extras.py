from urllib.parse import quote

from django import template

register = template.Library()


@register.filter(name="urlencode_full")
def urlencode_full(value):
    """URL-encode a full path segment, including slashes."""
    if value is None:
        return ""
    return quote(str(value), safe="")


@register.filter(name="splitlines")
def splitlines(value):
    """Split text into non-empty stripped lines for template iteration."""
    if not value:
        return []
    return [line.strip() for line in str(value).splitlines() if line.strip()]
