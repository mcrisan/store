from django.contrib.auth.signals import user_logged_in
from paypal.standard.ipn.signals import payment_was_successful
from django.contrib.auth.models import User

from .models import Cart, Product

def save_cart(sender, user, request, **kwargs):
    guest_user = User.objects.filter(username=request.session['user_id'][0:15], 
                                     last_name=request.session['user_id'][15:]).first()
    if guest_user:
        current_user = request.user    
        if guest_user.cart_set.exists():
            cart = Cart.from_user(current_user)
            cart_prod = guest_user.cart_set.first().cart_products_set.all()
            for prod in cart_prod:
                cart.check_product_cart(prod.product.id, prod.quantity)
                product = Product.objects.get(pk = prod.product.id)
                product.modify_quantity(0 - prod.quantity)
            guest_user.delete()  

user_logged_in.connect(save_cart)  

def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    if (ipn_obj.payment_status == "Completed") & (ipn_obj.flag==False):
        try:
            cart=Cart.objects.get(pk=ipn_obj.invoice)
            cart.create_order()
        except Cart.DoesNotExist:
            pass           

payment_was_successful.connect(show_me_the_money) 