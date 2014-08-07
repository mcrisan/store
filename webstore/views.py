import datetime
import json
import ipdb

from pprint import pprint
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.comments.forms import CommentForm
from django.contrib.comments import get_form
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.models import PayPalIPN
from social_auth.models import UserSocialAuth
from notifications import notify

from .forms import (RegisterForm, CartForm, RatingForm, ProductRatingsForm , 
                   DeliveryDetailsForm, UserEditForm, SearchForm, DiscountCodeForm)
from .models import (Cart, Product, Rating, DeliveryDetails, Discount, ProxyUser, options,
                     Category, WishList)
from .tasks import send_order_email
from .choices import DISCOUNT_STATUS_CHOICES, CART_STATUS_CHOICES
from django.conf import settings
from .helpers import get_user, check_user
   
def home(request, page=1):
    products = Product.objects.order_by('name').all()
    prod = Paginator(products, options.products_per_page)
    context = { "products" : prod.page(page), "type" : 2, "page_nr" : page}
    return render(request, "home.html", context)

def sort_by_name(request, type, page=1):
    if type == 'ASC':
        products = Product.objects.order_by('name').all()
        new_type = 'DESC'
    else:
        products = Product.objects.order_by('-name').all() 
        new_type = 'ASC'
    prod = Paginator(products, options.products_per_page)   
    context = {'products' : prod.page(page), 
               'type' : new_type, 
               'old_type' : type, 
               'page_nr' : page}
    return render(request, "home_sort_by_name.html", context)

def sort_by_popularity(request, type, page=1):
    if type == 'ASC':
        products = Product.objects.number_of_orders().order_by('num_orders')
        new_type = 'DESC'
    else:
        products = Product.objects.number_of_orders().order_by('-num_orders')
        new_type = 'ASC' 
    prod = Paginator(products, options.products_per_page)  
    context = { 'products' : prod.page(page),
                'type' : new_type, 
                'old_type' : type, 
                'page_nr' : page}
    return render(request, "home_sort_by_popularity.html", context)

def comment_form(request):
    error = request.GET.get('error', None)
    requestDict = {'error': error}
    return render_to_response('comments.html', 
                              requestDict, 
                              context_instance=RequestContext(request))

def post_comment(request):
    if request.method == 'POST':
        prod_id = request.POST['object_pk']
        prod = Product.objects.get(pk=prod_id)
        form = CommentForm(target_object=prod, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('store_home')
    else:
        form = CommentForm() 
    return render(request, "register.html", {'form': form})

def comment(request) :
    if request.method == 'POST' :
        prod_id = request.POST['object_pk']
        prod = Product.objects.get(pk=prod_id)
        post_values = request.POST.copy()
        post_values['name']= request.user.first_name + request.user.last_name
        post_values['email']= request.user.email
        comm_form = get_form()
        form = comm_form(target_object=prod, data=post_values)
        if (form.is_valid()) :
            form.save()  
        return HttpResponseRedirect(request.POST['next'])
    return HttpResponseRedirect('/')

def product_details(request, prod_id):
    try:
        product = Product.objects.get(pk=prod_id)
    except Product.DoesNotExist:
        messages.add_message(request, messages.INFO, 'We could not find the required product')
        return redirect('store_home')     
    context = { "product" : product}
    return render(request, "product.html", context)

@login_required
def rate_product(request):
    form = RatingForm(data=request.POST)
    if form.is_valid():
        data=request.POST
        current_user = request.user
        if current_user.has_ordered_product(data['prod_id']):
            rate = Rating.create_rate(current_user, data['prod_id'], data['rating'])
        avg_rate = Rating.from_product(data['prod_id'])
        context ={"rate": avg_rate} 
    else:
        context ={"mes": "Data is not valid"}      
    return HttpResponse(json.dumps(context), content_type="application/json") 

def product_rating(request):
    form = ProductRatingsForm(data=request.POST)
    ratings=[];
    if form.is_valid():
        data = request.POST.getlist('prod_id')      
        for prod_id in data:
            prod = Product.objects.get(pk=prod_id)
            rate = prod.product_rating()
            current_user = request.user
            wish = prod.is_on_wishlist(request.user)
            try:
                enable = current_user.has_ordered_product(prod_id)
            except AttributeError:
                enable = False    
            context = {"rate": rate,
                      "readonly" : not(enable),
                      "prod_id" : prod_id,
                      "wish" : wish} 
            ratings.append(context)     
    return HttpResponse(json.dumps(ratings), content_type="application/json")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('store_home')
    else:
        form = RegisterForm() 
    return render(request, "register.html", {'form': form})

def create_cart(request):
    form = CartForm(data=request.POST)
    if form.is_valid():
        data=request.POST
        current_user = get_user(request)    
        cart = Cart.from_user(current_user)
        prod, prod_cart = cart.check_product_cart(int(data['prod_id']), int(data['qty']))
        context ={"price": prod_cart.price,
                 "quantity": data['qty'],
                 "prod_id": data['prod_id'],
                 "stock" : prod.quantity,
                 "total_price" : cart.cart_amount()}
        notify.send(prod,
                    recipient=current_user,
                    verb=u'Has been added to your cart',
                    action_object=cart, 
                    description=u'We have updated your cart with the wanted product', 
                    )   
    context ={'cart': cart, 'price': cart.cart_amount()}      
    return render(request, "partials/sidebar/_cart.html", context)    

@csrf_exempt
def notifications(request):
    current_user = request.user
    notifications = current_user.notifications.all()
    i=0
    for notification in current_user.notifications.filter(unread=True):
        i +=1
        notification.mark_as_read()
    context ={'unread_count': i}       
    return render(request, "notifications.html", context)

@login_required
def delivery_details(request):
    current_user = request.user
    instance = DeliveryDetails.from_user(current_user)  
    if request.method == 'POST':       
        form = DeliveryDetailsForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('webstore:review_order')
    else:
        details = DeliveryDetails.latest_delivery_from_user(current_user)
        form = DeliveryDetailsForm(initial=details)
    return render(request, "delivery_details.html", {'form': form})

@login_required
def review_order(request):
    try:
        form_data = request.session.get('form_data', None)
        del request.session['form_data']
        form = DiscountCodeForm(form_data)
        form.is_valid()
    except KeyError:  
        form = DiscountCodeForm()  
    current_user = request.user
    cart = current_user.active_cart()
    if not cart:
        return redirect('store_home')    
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": cart.cart_amount(),
        "item_name": "webstore cart",
        "invoice": cart.id,
        "quantity": 1,
        #"notify_url": "http://127.0.0.1:8000" + reverse('paypal-ipn'),
        "notify_url": "http://5f1a21b4.ngrok.com" + reverse('paypal-ipn'), 
        "return_url": "http://localhost:8000" + reverse("success"),
        "cancel_return": "http://localhost:8000" + reverse("canceled"),

    }
    pform = PayPalPaymentsForm(initial=paypal_dict)
    context = {"pform": pform}                 
    return render(request, "review_order.html", {'cart':cart, 'form':form, "pform": pform}) 

def remove_coupon(request):
    current_user = request.user
    cart = current_user.active_cart()
    if not cart:
        return redirect('store_home')
    else:
        cart.remove_coupon()
        messages.add_message(request, messages.INFO, 'Your coupon was removed')
        return redirect('webstore:review_order')
    
def apply_coupon(request):    
    if request.method == 'POST':
        current_user = request.user
        cart = current_user.active_cart()      
        form = DiscountCodeForm(data=request.POST)
        if form.is_valid():
            coupon = cart.apply_discount(form.data['code'])
            if coupon: 
                notify.send(coupon,
                    recipient=request.user,
                    verb=u'has been applied',
                    action_object=cart, 
                    description=u'We have updated your cart with the wanted product', 
                )
                messages.add_message(request, 
                                     messages.INFO, 
                                     'Your coupon has been applied to products in promotion')
            else:
                messages.add_message(request, messages.INFO, 'Your coupon is not valid')
        else:
            request.session['form_data'] = request.POST        
    return redirect('webstore:review_order')
         
def payment_success(request):
    txn = request.GET.get('tx', None) 
    try:   
        order = PayPalIPN.objects.get(txn_id=txn)
    except PayPalIPN.DoesNotExist: 
        messages.add_message(request, messages.INFO, 'We could not locate your transaction')
        return redirect('webstore:review_order') 
    else:        
        cart = Cart.objects.get(pk=order.invoice)
        if cart.status == CART_STATUS_CHOICES.ORDERED:
            notify.send(cart,
                recipient=request.user,
                verb=u'order has been processed',
                action_object=cart, 
                description=u'We have updated your cart with the wanted product', 
            )
            messages.add_message(request, messages.INFO, 'Your transaction was processed')
            return redirect('webstore:order_details', cart_id=cart.id) 
        else: 
            messages.add_message(request, messages.INFO, 'Your transaction is being processed') 
            return redirect('webstore:review_order')              

def payment_canceled(request):
    messages.add_message(request, messages.INFO, 'Payment was canceled')
    return redirect('webstore:review_order')   

@login_required
def checkout(request):
    current_user = request.user
    cart = current_user.active_cart()
    if cart:
        cart.create_order() 
        messages.add_message(request, messages.INFO, 'Your order was created')
        send_order_email.delay(request.user)
        return redirect('webstore:order_details', cart_id=cart.id)
    else:
        messages.add_message(request, messages.INFO, 'We could not create your order order')
        return redirect('store_home')


def delete_prod(request, prod_id):
    current_user = get_user(request)
    cart = current_user.active_cart()
    if cart:
        prod = cart.get_product(prod_id)
        if prod:
            product =prod.product
            product.modify_quantity(0 - prod.quantity)
            prod.remove_coupon()
            prod.delete()
            messages.add_message(request, messages.INFO, 'Product was deleted')                            
    return redirect('store_home')

@login_required
def user_orders(request):
    current_user = request.user
    cart =current_user.orders()
    return render(request, "user_orders.html", {'cart': cart})

@login_required
def order_details(request, cart_id):
    current_user = request.user
    try:
        order =current_user.order(cart_id)
    except AttributeError:
        messages.add_message(request, messages.INFO, 'We could not find the required order')
        return redirect('store_home')                               
    return render(request, "order_details.html", {'order': order})

def edit_account(request):
    current_user = request.user 
    if request.method == 'POST':       
        form = UserEditForm(data=request.POST, instance=current_user)
        if form.is_valid():
            form.save()
            return redirect('store_home')
    else:
        form = UserEditForm(instance=current_user) 
    return render(request, 'edit_user.html',{'form':form})

def offers(request):
    offers =Discount.objects.active_discounts()
    return render(request, "offers.html", {'offers':offers})

def offer_details(request, offer_id):
    try:
        offer =Discount.objects.get(pk=offer_id)
    except Discount.DoesNotExist:
        messages.add_message(request, messages.INFO, 'We could not find the offer')
        return redirect('webstore:offers')    
    return render(request, "offer_details.html", {'offer':offer})

def search(request):
    if request.method == 'POST':       
        form = SearchForm(data=request.POST)
        if form.is_valid():
            products = Product.objects.search(form.data['query'])
            context = { "products" : products, "query" : form.data['query']}
            return render(request, "search.html", context)
    else: 
        return redirect('store_home')
    
def products_categories(request, name, page=1):
    try:
        category=Category.objects.get(name=name)
    except Category.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Required category was not found')
        return redirect('store_home')    
    products = category.products.all()
    prod = Paginator(products, options.products_per_page)
    context = { "products" : prod.page(page), 
               "type" : 2, 
               "page_nr" : page, 
               "name": category.name}
    return render(request, "categories.html", context)

@csrf_exempt
def add_to_wishlist(request, prod_id):
    current_user = request.user
    wishlist = WishList.from_user(current_user)
    data=[]
    try:
        product = Product.objects.get(pk=prod_id)
        message = wishlist.add_to_wishlist(product)
        context = {'href' : reverse('webstore:remove_from_wishlist', kwargs={'prod_id':prod_id} ),
                   'text' : "Remove from wishlist!",
                   'message' : message,
                   }
        data.append(context)
    except Product.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Product does not exist')
    return HttpResponse(json.dumps(context), content_type="application/json")

@csrf_exempt
def remove_from_wishlist(request, prod_id):
    current_user = request.user
    wishlist = WishList.from_user(current_user)
    data=[]
    try:
        product = Product.objects.get(pk=prod_id)
        message = wishlist.remove_from_wishlist(product)
        context = {'href': reverse('webstore:add_to_wishlist', kwargs={'prod_id':prod_id}),
                   'text': "Add to wishlist!",
                   'message' : message,
                }
        data.append(context)
    except Product.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Product does not exist')
    return HttpResponse(json.dumps(context), content_type="application/json") 

def wishlist_products(request, page=1): 
    products = request.user.wishlist.products.all()
    prod = Paginator(products, options.products_per_page)
    context = { "products" : prod.page(page), "type" : 2, "page_nr" : page}
    return render(request, "wish_list.html", context)
    
