from django import template

register = template.Library()

@register.filter(name='replace_line_br')
def replace_line_br(value):
    return value.replace("\n", "<br>")

@register.filter(name='show_author_list')
def show_author_list(value):
    return ', '.join(value.split("\n"))

@register.filter(name='split')
def split(value, sep):
    return value.split(sep)

@register.filter(name='splitlines')
def splitlines(value):
    return value.splitlines()
