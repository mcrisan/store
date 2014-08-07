from django import template

register = template.Library()

@register.filter(name='is_on_wishlist')
def is_on_wishlist(obj, user):
    return obj.is_on_wishlist(user)

@register.filter(name='discounted_price')
def discounted_price(obj, user):
    return obj.discounted_price(user)

@register.filter(name='discount')
def discount(obj, user):
    return obj.discount(user)

