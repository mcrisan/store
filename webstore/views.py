from django.shortcuts import render
from django.http import HttpResponse

from webstore.models import Product

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
