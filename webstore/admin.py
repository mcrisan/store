import datetime
import ipdb

from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType

from .models import Category, Product, Cart, Cart_Products, Rating, Discount, UserMethods


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        exclude = ('status',)
    
    def clean_percent(self):
        if self.cleaned_data['percent'] < 1:
            raise forms.ValidationError("Percent must be at least 1")
        if self.cleaned_data['percent'] > 100:
            raise forms.ValidationError("Percent must be under 100")
        return self.cleaned_data['percent']  
    
    def clean_end_date(self): 
        if 'start_date' in self.cleaned_data: 
            if self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
                raise forms.ValidationError("End date must be higher than start date")
            return self.cleaned_data['end_date'] 
  
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
    
    def clean_quantity(self):
        if self.cleaned_data['quantity'] < 1:
            raise forms.ValidationError("Quantity must be at least 1")
        return self.cleaned_data['quantity']  
    
    def clean_price(self):       
        if self.cleaned_data['price'] <= 0:
            raise forms.ValidationError("Price should be over 0")
        return self.cleaned_data['price'] 
    
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
    
    def clean_value(self):
        if self.cleaned_data['value'] < 0 | self.cleaned_data['value'] > 5:
            raise forms.ValidationError("Rating must be between 1 and 5")
        return self.cleaned_data['value']            
      

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    form = ProductForm
   

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1  
    form = RatingForm  
 
    
class Cart_Products(admin.TabularInline):
    model = Cart_Products
    extra = 1    


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ['name']
    inlines = [ProductInline]


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'price', 
                    'quantity_ordered', 'total_orders', 'product_rating')
    search_fields = ['name']
    inlines = [RatingInline]
    form = ProductForm


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent', 'start_date', 'end_date', 'status')
    search_fields = ['name']
    filter_horizontal = ('products',)
    form = DiscountForm
  
    
class CartAdmin(admin.ModelAdmin):
    model = Cart
    list_display = ('user','cart_amount', 'cart_quantity', 'cart_nr_products', 
                    'cart_latest_update', 'status')
    inlines = [Cart_Products]   
    list_filter = ('status', )
    
class UserMethodsAdmin(admin.ModelAdmin):
    model = UserMethods
    actions = None
    list_display = ('username', 'money_spent', 'products_ordered', 'latest_order', 'first_order')  
     
    def has_add_permission(self, request):
        # Nobody is allowed to add
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Nobody is allowed to delete
        return False
    
    def __init__(self, *args, **kwargs):
        super(UserMethodsAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, ) 

    #readonly_fields = ('money_spent', 'products_ordered', 'latest_order', 'first_order')
    #readonly_fields = User._meta.get_all_field_names()
    
#    def has_change_permission(self, request, obj=None):
#        return False
    
class CustomUserAdmin(UserAdmin):
    model = UserMethods
    
    def view_link(self,obj):
      url = reverse('user_data', kwargs={'user_id': obj.id})
      return u"<a href='{0}'>View</a>".format(url)
    view_link.short_description = 'View Details'
    view_link.allow_tags = True
    
    def get_admin_url(self,obj):
        url = reverse("admin:webstore_usermethods_changelist")
        return u"<a href='{0}'>View</a>".format(url)
    get_admin_url.short_description = 'View Details'
    get_admin_url.allow_tags = True
    
    def queryset(self, request):
        return self.model.objects.all().exclude(first_name='Anonymous')
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff', 'get_admin_url')
   

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserMethods, UserMethodsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Discount, DiscountAdmin)


@staff_member_required
def users_stats(request):
    users = UserMethods.objects.all().exclude(first_name='Anonymous')
    total_orders_price = Cart.objects.orders_total_price()
    total_number_orders = Cart.objects.total_orders()
    total_products_ordered = Cart.objects.total_products_ordered()
    average_price_order = total_orders_price / total_number_orders
    average_items_order = total_products_ordered / total_number_orders
    average_orders_user = total_number_orders / len(users)
    return render(request, "admin/user_statistics.html",
                   {'users'               : users,
                    'orders_price'        : total_orders_price,
                    'number_orders'       : total_number_orders,
                    'products_ordered'    : total_products_ordered,
                    'average_price_order' : average_price_order,
                    'average_items_order' : average_items_order,
                    'average_orders_user' : average_orders_user
                    })

@staff_member_required
def user_data(request, user_id):
    try:
        user = UserMethods.objects.get(pk=user_id)
    except: 
        return redirect('admin:index')        
    return render(request, "admin/user_orders.html", {'user':user})