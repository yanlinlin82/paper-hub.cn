from django import template
import re

register = template.Library()

@register.filter(name='replace_line_br')
def replace_line_br(value):
    return value.replace("\n", "<br><br>")

@register.filter(name='is_for_xiangma')
def is_for_xiangma(value):
    return re.match("^/xiangma/", value)
