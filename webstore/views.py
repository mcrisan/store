import datetime
import json
import ipdb

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.comments.forms import CommentForm
from django.contrib.comments import get_form

from .forms import (RegisterForm, CartForm, RatingForm, ProductRatingsForm , 
                   DeliveryDetailsForm, UserEditForm, SearchForm, DiscountCodeForm)
from .models import Cart, Product, Rating, DeliveryDetails, Discount, UserMethods, options
from .tasks import send_order_email
from .choices import DISCOUNT_STATUS_CHOICES, CART_STATUS_CHOICES
 
   
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
        products = (Product.objects.annotate(num_orders=Count('cart_products'))
                                  .order_by('num_orders').all())
        new_type = 'DESC'
    else:
        products = (Product.objects.annotate(num_orders=Count('cart_products'))
                                  .order_by('-num_orders').all())
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
    return render_to_response('comments.html', requestDict, context_instance=RequestContext(request))

def post_comment(request):
    if request.method == 'POST':
        prod_id = request.POST['object_pk']
        print prod_id
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
        print prod_id
        prod = Product.objects.get(pk=prod_id)
        post_values = request.POST.copy()
        post_values['name']= request.user.first_name + request.user.last_name
        post_values['email']= request.user.email
        comm_form = get_form()
        form = comm_form(target_object=prod, data=post_values)
        if (form.is_valid()) :
            form.save()
        ipdb.set_trace()   
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
        if current_user.cart_set.filter(products__id=data['prod_id'], status='1').exists():
            rate = Rating.create_rate(current_user, data['prod_id'], data['rating'])
            rate.save()
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
            try:
                enable = (current_user.cart_set.filter(products__id=prod_id, 
                                                       status=CART_STATUS_CHOICES.ORDERED)
                                              .exists())
            except AttributeError:
                enable = False    
            context = {"rate": rate,
                      "readonly" : not(enable),
                      "prod_id" : prod_id} 
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
    return HttpResponse(json.dumps(context), content_type="application/json") 

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
    form = DiscountCodeForm() 
    current_user = request.user
    cart = current_user.cart_set.filter(status=CART_STATUS_CHOICES.ACTIVE).first()
    if not cart:
        return redirect('store_home')
    if request.method == 'POST':      
        form = DiscountCodeForm(data=request.POST)
        if form.is_valid():
            cart.apply_discount(form.data['code'])  
            messages.add_message(request, messages.INFO, 'Your coupon has been applied')           
    return render(request, "review_order.html", {'cart':cart, 'form':form})     

@login_required
def checkout(request):
    current_user = request.user
    cart = current_user.cart_set.filter(status=CART_STATUS_CHOICES.ACTIVE).first()
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
    cart =Cart.objects.filter(user=current_user, status=CART_STATUS_CHOICES.ACTIVE).first()
    if cart:
        prod = cart.cart_products_set.filter(product__id=prod_id).first()
        if prod:
            product = Product.objects.get(pk = prod_id)
            product.modify_quantity(0 - prod.quantity)
            prod.remove_dicount()
            prod.delete()
            messages.add_message(request, messages.INFO, 'Product was deleted')                            
    return redirect('store_home')

@login_required
def user_orders(request):
    current_user = request.user
    cart =Cart.objects.filter(user=current_user, status=CART_STATUS_CHOICES.ORDERED).all()                         
    return render(request, "user_orders.html", {'cart': cart})

@login_required
def order_details(request, cart_id):
    current_user = request.user
    try:
        products = (Cart.objects.filter(id=cart_id, 
                                        user=request.user, 
                                        status=CART_STATUS_CHOICES.ORDERED)
                              .first().cart_products_set.all())
    except AttributeError:
        messages.add_message(request, messages.INFO, 'We could not find the required order')
        return redirect('store_home')                               
    return render(request, "order_details.html", {'products': products})

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
    offers =Discount.objects.filter(status=CART_STATUS_CHOICES.ACTIVE)
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
            products = Product.objects.filter(name__icontains=form.data['query'])
            context = { "products" : products, "query" : form.data['query']}
            return render(request, "search.html", context)
    else: 
        return redirect('store_home')

def load_sidebar_cart(request):
    context = {}      
    current_user = check_user(request)
    if hasattr(current_user, 'cart_set') and current_user.cart_set.count()>0:
        if current_user.cart_set.last().status == CART_STATUS_CHOICES.ACTIVE:
            cart = current_user.cart_set.last()    
            context['price'] = cart.cart_amount() 
            context['prod'] = cart.cart_products_set.all()   
    return context

def load_sidebar_search(request):     
    form = SearchForm() 
    promoform = DiscountCodeForm()
    context = {'form' : form} 
    return context

def get_user(request):
    current_user = check_user(request)
    if not current_user:
        current_user = User(username=request.session['user_id'][0:15], 
                            first_name='Anonymous', 
                            last_name=request.session['user_id'][15:])
        current_user.set_unusable_password()
        current_user.save()
    return current_user 

def check_user(request):
    if request.user.is_authenticated():
        current_user = request.user
    else:
        try:
            current_user = (User.objects.filter(username=request.session['user_id'][0:15], 
                                                last_name=request.session['user_id'][15:])
                                       .first())
        except KeyError:
           current_user=None 
    return current_user 

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