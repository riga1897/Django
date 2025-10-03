from django import template

register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "#"


@register.filter(name='widget_type')
def widget_type(field):
    """Returns the widget class name for template conditionals"""
    return field.field.widget.__class__.__name__