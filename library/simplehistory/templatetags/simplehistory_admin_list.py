from django import template

register = template.Library()


@register.inclusion_tag("simplehistory/_object_history_list.html", takes_context=True)
def display_list(context):
    return context
