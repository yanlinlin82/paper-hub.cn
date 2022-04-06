from django import template
import re

register = template.Library()

@register.filter(name='replace_line_br')
def replace_line_br(value):
    return value.replace("\n", "<br>")

@register.filter(name='is_for_xiangma')
def is_for_xiangma(value):
    return re.match("^/xiangma/", value)

@register.filter(name='show_author_list')
def show_author_list(value):
    return ', '.join(value.split("\n"))

@register.filter(name='split')
def split(value, sep):
    return value.split(sep)

@register.filter(name='splitlines')
def splitlines(value):
    return value.splitlines()

@register.filter(name='identify_labels')
def identify_labels(value):
    return re.sub(r'#(\S+)', r'<div class="label"><a href="/view/label/\1">#\1</a></div>', value)
