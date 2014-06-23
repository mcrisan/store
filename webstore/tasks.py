from __future__ import absolute_import

import datetime

from datetime import timedelta
from django.db.models import Max
from celery import shared_task

from webstore.models import Cart, Product, User, options as opt

@shared_task
def removecart():
    print "removing carts"
    date=datetime.datetime.now()-timedelta(days=opt.remove_cart)
    carts = Cart.objects.annotate(total=Max('cart_products__date_added')).filter(total__lt=date, status='0').all()
    for cart in carts:
        for prod in cart.cart_products_set.all():
            product = Product.objects.get(pk = prod.product.id)
            product.modify_quantity(0 - prod.quantity)
        cart.delete()
        
@shared_task
def remove_guest_accounts():
    print "removing guest accounts"
    date=datetime.datetime.now()-timedelta(days=1)
    users = User.objects.filter(last_login__lt=date, first_name='Anonymous').all()
    for user in users:
        user.delete()
        