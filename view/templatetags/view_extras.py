from django import template
from urllib.parse import quote

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
