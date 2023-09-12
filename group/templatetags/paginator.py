from django import template
from django.core.paginator import Paginator

register = template.Library()

@register.simple_tag
def get_elided_page_range(p, number):
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(number=number)
