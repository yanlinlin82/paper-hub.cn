from django import template

register = template.Library()

@register.filter(name='replace_line_br')
def replace_line_br(value):
    return value.replace("\n", "<br><br>")
