from __future__ import absolute_import

import datetime

from datetime import timedelta
from django.db.models import Max
from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from webstore.models import Cart, Product, User, options as opt
from store.settings import EMAIL_HOST_USER

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
        
@shared_task
def send_order_email(to_user):
    products =to_user.cart_set.filter(status='1').last().cart_products_set.all()
    cart_amount = to_user.cart_set.filter(status='1').last().cart_amount()
    plaintext = get_template('emails/order.txt')
    htmly     = get_template('emails/order.html')
    d = Context({ 'products': products, 'user': to_user, 'price': cart_amount })
    subject="We have received your order"
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [to_user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
        