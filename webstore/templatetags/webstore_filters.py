from django import template

register = template.Library()

@register.filter(name='is_on_wishlist')
def is_on_wishlist(obj, user):
    return obj.is_on_wishlist(user)

