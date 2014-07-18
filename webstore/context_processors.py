from .helpers import check_user
from .choices import CART_STATUS_CHOICES
from .models import Category
from .forms import SearchForm
                   
def load_sidebar_cart(request):
    context = {}      
    current_user = check_user(request)
    if hasattr(current_user, 'cart_set') and current_user.cart_set.count()>0:
        if current_user.cart_set.last().status == CART_STATUS_CHOICES.ACTIVE:
            cart = current_user.cart_set.last()    
            context['price'] = cart.cart_amount() 
            context['cart'] = cart 
    return context

def load_sidebar_search(request):     
    form = SearchForm() 
    context = {'form' : form} 
    return context

def load_categories(request):     
    categories = Category.objects.all()
    context = {'categories' : categories} 
    return context