import datetime

from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.db.models import Max

from webstore.models import Cart, Product, options as opt

class Command(BaseCommand):
    args = ''
    help = 'Remove carts without activity'

    def handle(self, *args, **options):
        date=datetime.datetime.now()+timedelta(days=opt.remove_cart)
        carts = Cart.objects.annotate(total=Max('cart_products__date_added')).filter(total__gt=date).all()
        for cart in carts:
            for prod in cart.cart_products_set.all():
                product = Product.objects.get(pk = prod.product.id)
                product.modify_quantity(0 - prod.quantity)
            cart.delete()
            

