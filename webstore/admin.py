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
from django.db.models import Count, Sum, Max, Min
from django.contrib.admin import SimpleListFilter

from .models import Category, Product, Cart, Cart_Products, Rating, Discount, ProxyUser, Coupon
from .choices import CART_STATUS_CHOICES


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
 
    
class Cart_ProductsInline(admin.TabularInline):
    model = Cart_Products
    extra = 1  
    
    
class UserFilter(SimpleListFilter):
    title = 'latest user' 
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        users = set([u.user for u in model_admin.model.objects.all()])
        date=datetime.datetime.now()-datetime.timedelta(days=1)
        return [(u.id, u.username) for u in users if u.last_login>date][:3]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id__exact=self.value())
        else:
            return queryset    
 
    
class Cart_ProductsAdmin(admin.ModelAdmin):
    def discount_value(self,obj):
        if obj.discount:
            return obj.discount.percent
        else:
            return 0
    discount_value.short_description = 'Discount Value'
    
    list_display = ('product', 'quantity', 'price', 
                    'date_added', 'discount_value')
    search_fields = ['name']     
    list_filter = ('discount__percent', 'cart__user', 'product__category')


class CategoryAdmin(admin.ModelAdmin):
    def products_category(self, obj):
        if obj.products_category()>0:
            url =reverse("admin:webstore_product_changelist")
            lookup = u"category__id__exact"
            text = obj.products_category()
            return u"<a href='%s?%s=%s'>%s</a>" % (url, lookup, obj.id, text) 
        else:   
            return 0
    products_category.allow_tags = True
    products_category.short_description = 'Products'
    
    def quantity_ordered(self, obj):
        if obj.quantity_ordered()>0:
            url =reverse("admin:webstore_cart_products_changelist")
            lookup = u"product__category__id__exact"
            text = obj.quantity_ordered()
            return u"<a href='%s?%s=%s'>%s</a>" % (url, lookup, obj.id, text) 
        else:   
            return 0
    quantity_ordered.allow_tags = True
    quantity_ordered.short_description = 'Quantity Ordered'
    
    list_display = ('name', 'products_category', 'quantity_ordered', 'revenue')
    search_fields = ['name']
    inlines = [ProductInline]


class ProductAdmin(admin.ModelAdmin): 
    def product_discount(self, obj):
        if obj.promotion():
            discount = obj.promotion().name
            if(hasattr(obj.promotion(), 'discount')):
                url =reverse("admin:webstore_discount_changelist")
            else:
                url =reverse("admin:webstore_coupon_changelist")    
            lookup = u"name"
            text = discount
            return u"<a href='%s?%s=%s'>%s</a>" % (url, lookup, obj.promotion().name, text) 
        else:   
            return None
    product_discount.allow_tags = True
    product_discount.short_description = 'Product discount'
    
    def product_orders(self, obj):
        if obj.total_orders():
            discount = obj.promotion().name
            url =reverse("admin:webstore_cart_changelist")
            lookup = u"cart_products__product"
            text = obj.total_orders()
            return u"<a href='%s?%s=%s'>%s</a>" % (url, lookup, obj.id, text) 
        else:    
            return None
    product_orders.allow_tags = True
    product_orders.short_description = 'Product orders'
        
    list_display = ('name', 'quantity', 'price', 'quantity_ordered', 
                    'revenue', 'product_orders', 'product_rating', 'product_discount')
    search_fields = ['name']
    inlines = [RatingInline]
    form = ProductForm
    list_filter = ( 'promotion', 'category')  

class PromotionAdmin(admin.ModelAdmin):
    def products_offer(self, obj):
        url =reverse("admin:webstore_product_changelist")
        lookup = u"promotion__id__exact"
        text = u"View Products"
        return u"<a href='%s?%s=%d'>%s</a>" % (url, lookup, obj.pk, text)
    products_offer.allow_tags = True
    products_offer.short_description = 'Products in Offer'
    
    def products_ordered(self, obj):
        url =reverse("admin:webstore_cart_products_changelist")
        lookup = u"discount__id__exact"
        text = u"View Products"
        return u"<a href='%s?%s=%d'>%s</a>" % (url, lookup, obj.pk, text)
    products_ordered.allow_tags = True
    products_ordered.short_description = 'Products Ordered'


class DiscountAdmin(PromotionAdmin):       
    list_display = ('name', 'percent', 'start_date', 'end_date', 'status', 
                    'products_offer', 'quantity_ordered', 'money_spent', 
                    'real_value', 'products_ordered')
    search_fields = ['name']
    filter_horizontal = ('products',)
    form = DiscountForm
    list_filter = ('status', 'cart_products__cart__user', 'name') 
  
    
class CartAdmin(admin.ModelAdmin):
    model = Cart
    
    def cart_products(self, obj):
        url =reverse("admin:webstore_cart_products_changelist")
        cart_lookup = u"cart__exact"
        status = u"status__exact"
        text = u"View Products"
        return u"<a href='%s?%s=%d'>%s</a>" % (url, cart_lookup, obj.pk, text)
    cart_products.allow_tags = True
    cart_products.short_description = 'Products in Order'
    
    def discounted_products(self, obj):
        url =reverse("admin:webstore_cart_products_changelist")
        discount_lookup = u"discount__isnull"
        cart_lookup = u"cart__id__exact"
        text = u"View Products"
        return u"<a href='%s?%s=%d&%s=%d'>%s</a>" % (url, 
                                                     discount_lookup, 
                                                     False, 
                                                     cart_lookup, 
                                                     obj.id, 
                                                     text)
    discounted_products.allow_tags = True
    discounted_products.short_description = 'Discounted Products'
    
    list_display = ('user','cart_amount', 'cart_quantity', 'cart_nr_products', 
                    'cart_latest_update', 'status', 'cart_products', 'discounted_products')
    inlines = [Cart_ProductsInline]   
    list_filter = ('status', UserFilter, 'cart_products__product' )
 
    
class ProxyUserAdmin(admin.ModelAdmin):
    model = ProxyUser
    actions = None
    
    def number_of_orders(self,obj):
        return len(obj.orders())
    number_of_orders.admin_order_field = 'ordersc'
    
    def queryset(self, request):
        qs = super(ProxyUserAdmin, self).queryset(request)
        qs = qs.annotate(ordersc=Count('cart__user'))
        qs = qs.annotate(total_amount=Sum('cart__cart_products__price'))
        qs = qs.annotate(nr_prod=Sum('cart__cart_products__quantity'))
        qs = qs.annotate(latest=Max('cart__cart_products__date_added'))
        qs = qs.annotate(first=Min('cart__cart_products__date_added'))
        return qs
    
    def average_prod_order(self,obj):
        if self.number_of_orders(obj)>0:
            average_prod_order=obj.products_ordered()/self.number_of_orders(obj)
        else:
            average_prod_order=0.0
        return average_prod_order
    average_prod_order.short_description = 'Products/Order'
    
    def average_money_order(self,obj):
        if self.number_of_orders(obj)>0:
            average_money_order=obj.money_spent()/self.number_of_orders(obj)
        else:
            average_money_order=0.0
        return average_money_order
    average_money_order.short_description = 'Money/Order'
    
    def offers_used(self, obj):
        url =reverse("admin:webstore_discount_changelist")
        lookup = u"cart_products__cart__user__id__exact"
        text = u"View Offers"
        return u"<a href='%s?%s=%d'>%s</a>" % (url, lookup, obj.pk, text)
    offers_used.allow_tags = True
        
    list_display = ('username', 'money_spent', 'products_ordered', 'latest_order', 
                    'first_order', 'offers_claimed', 'number_of_orders', 
                    'average_prod_order', 'average_money_order', 'offers_used')  
     
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def __init__(self, *args, **kwargs):
        super(ProxyUserAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, ) 
  
    
class CustomUserAdmin(UserAdmin):
    model = ProxyUser
    
    def view_link(self,obj):
      url = reverse('user_data', kwargs={'user_id': obj.id})
      return u"<a href='{0}'>View</a>".format(url)
    view_link.short_description = 'View Details'
    view_link.allow_tags = True
    
    def get_admin_url(self,obj):
        url = reverse("admin:webstore_proxyuser_changelist")
        return u"<a href='{0}'>View</a>".format(url)
    get_admin_url.short_description = 'View Details'
    get_admin_url.allow_tags = True
    
    def products_bought(self, obj):
        url =reverse("admin:webstore_cart_products_changelist")
        lookup = u"cart__user__id__exact"
        text = u"View Products"
        return u"<a href='%s?%s=%d'>%s</a>" % (url, lookup, obj.pk, text)
    products_bought.allow_tags = True
    
    def orders(self, obj):
        url =reverse("admin:webstore_cart_changelist")
        lookup = u"user"
        status = u"status__exact"
        text = u"View Orders"
        return u"<a href='%s?%s=%d&%s=%s'>%s</a>" % (url, 
                                                     lookup, 
                                                     obj.pk, 
                                                     status, 
                                                     CART_STATUS_CHOICES.ORDERED, 
                                                     text)
    orders.allow_tags = True
    
    def queryset(self, request):
        return self.model.objects.all().exclude(first_name='Anonymous')
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 
                    'date_joined', 'is_staff', 'get_admin_url', 'orders', 
                    'products_bought')
    
class CouponAdmin(PromotionAdmin):
       
    list_display = ('name', 'percent', 'start_date', 'status', 
                    'products_offer', 'quantity_ordered', 'money_spent', 
                    'real_value', 'products_ordered','volume','code', 'first_order')
    search_fields = ['name']
    filter_horizontal = ('products',)
    form = DiscountForm
    list_filter = ('status', 'cart_products__cart__user', 'name')    
   

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ProxyUser, ProxyUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Cart_Products, Cart_ProductsAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Coupon, CouponAdmin)
