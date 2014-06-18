import datetime
import json
import ipdb

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .forms import RegisterForm, CartForm, RatingForm, ProductRatingsForm 
from .models import Cart, Product, Rating

def home(request):
    products = Product.objects.order_by('name').all()
    context = { "products" : products, "type" : 2}
    return render(request, "home.html", context)

def sort_by_name(request, type):
    if type == '0':
        products = Product.objects.order_by('name').all()
    else:
        products = Product.objects.order_by('-name').all()  
    context = { "products" : products, 'type' : int(not int(type))}
    return render(request, "home.html", context)

def sort_by_popularity(request, type):
    if type == '0':
        products = Product.objects.annotate(num_orders=Count('cart_products')).order_by('num_orders').all()
    else:
        products = Product.objects.annotate(num_orders=Count('cart_products')).order_by('-num_orders').all()  
    context = { "products" : products, 'type' : int(not int(type))}
    return render(request, "home.html", context)

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
        rating = int(data['rating'])
        prod_id = int(data['prod_id'])
        current_user = request.user
        if current_user.cart_set.filter(products__id=prod_id, status='1').exists():
            rate = Rating.create_rate(current_user, prod_id, rating)
            rate.save()
        avg_rate = Rating.from_product(prod_id)
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
                enable = current_user.cart_set.filter(products__id=prod_id, status='1').exists()
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

@login_required
def create_cart(request):
    form = CartForm(data=request.POST)
    if form.is_valid():
        data=request.POST
        quantity = int(data['qty'])
        product_id = int(data['prod_id'])
        current_user = request.user
        cart = Cart.from_user(current_user)
        prod, prod_cart = cart.check_product_cart(product_id, quantity)
        context ={"price": prod_cart.price,
                 "quantity": quantity,
                 "prod_id": product_id,
                 "stock" : prod.quantity,
                 "total_price" : cart.cart_amount()}   
    return HttpResponse(json.dumps(context), content_type="application/json") 

@login_required
def checkout(request):
    if request.user.is_authenticated():
        current_user = request.user
        cart =Cart.objects.filter(user=current_user, status='0').first()
        if cart:
            cart.status = '1'
            cart.save()      
    return redirect('store_home')

@login_required
def delete_prod(request, prod_id):
    current_user = request.user
    cart =Cart.objects.filter(user=current_user, status='0').first()
    if cart:
        prod = cart.cart_products_set.filter(product__id=prod_id).first()
        if prod:
            product = Product.objects.get(pk = prod_id)
            product.modify_quantity(0 - prod.quantity)
            prod.delete()
            messages.add_message(request, messages.INFO, 'Product was deleted')                            
    return redirect('store_home')

@login_required
def user_orders(request):
    current_user = request.user
    cart =Cart.objects.filter(user=current_user, status='1').all()                         
    return render(request, "user_orders.html", {'cart': cart})

@login_required
def order_details(request, cart_id):
    current_user = request.user
    try:
        products =Cart.objects.filter(id=cart_id, user=request.user, status='1').first().cart_products_set.all()
    except AttributeError:
        messages.add_message(request, messages.INFO, 'We could not find the required order')
        return redirect('store_home')                                 
    return render(request, "order_details.html", {'products': products})

@login_required
def load_sidebar_cart(request):
    context = {}      
    current_user = request.user
    if current_user.cart_set.count()>0:
        if current_user.cart_set.last().status == '0':
            cart = current_user.cart_set.last()    
            context['price'] = cart.cart_amount() 
            context['prod'] = cart.cart_products_set.all()   
    return context