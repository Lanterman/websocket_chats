from django import template

register = template.Library()


@register.filter(name="sum_unread_messages")
def sum_unread_messages(value):
    """Sum unread messages tag"""
    return len(value)
