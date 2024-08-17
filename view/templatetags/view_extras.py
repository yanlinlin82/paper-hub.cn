import re
from urllib.parse import quote
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import bleach
import html

register = template.Library()

@register.filter(name='replace_line_br')
def replace_line_br(value):
    return value.replace("\n", "<br>")

@register.filter(name='show_author_list')
def show_author_list(value):
    return ', '.join(value.split("\n"))

@register.filter(name='split')
def split(value, sep):
    return [k for k in value.split(sep) if k]

@register.filter(name='splitlines')
def splitlines(value):
    return value.splitlines()

@register.filter
def urlencode_full(value):
    return quote(value, safe='') # 'abc/def' => 'abc%2Fdef'

@register.filter(name='custom_escape')
def custom_escape(html_input):
    unescaped_input = html.unescape(html_input)
    allowed_tags = ['b', 'i', 'u', 'a', 'strong', 'em']
    clean_html = bleach.clean(unescaped_input, tags=allowed_tags, strip=True)
    return mark_safe(clean_html)
