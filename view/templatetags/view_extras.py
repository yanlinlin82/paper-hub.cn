import re
from django import template
from django.urls import reverse

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

def label_replace(match, request):
    m = match.group(1)
    m2 = re.sub('/', '+', m)
    s = '<div class="label"><a href="' + reverse('view:label', kwargs={'name': m2}, current_app=request.resolver_match.namespace) + '">#' + m + '</a></div>'
    return re.sub('\n', '<br>', s)

@register.simple_tag(name='format_comments', takes_context=True)
def format_comments(context, value):
    return re.sub(r'#([^\s:#\'\"]+)', lambda line: label_replace(line, context['request']), value)
