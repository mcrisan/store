from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User

from webstore.models import Product
from .forms import RegisterForm 

# Create your views here.
def index(request):
    print "456"
    return HttpResponse("Hello, world. You're at the poll index.")

def home(request):
    products = Product.objects.all()
    context = { "products" : products}
    print context
    for product in context['products']:
        print product
    return render(request, "home.html", context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            data=request.POST
            user = User()
            user.username = data['username']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.set_password(data['password'])
            user.save()
            return redirect('store_home')
    else:
        form = RegisterForm() 
    return render(request, "register.html", {'form': form})