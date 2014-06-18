from django.contrib import admin

from .models import Category, Product, Cart, Cart_Products, Rating


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1    
 
    
class Cart_Products(admin.TabularInline):
    model = Cart_Products
    extra = 1    


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ['name']
    inlines = [ProductInline]


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'price', 'quantity_ordered', 'total_orders', 'product_rating')
    search_fields = ['name']
    inlines = [RatingInline]
  
    
class CartAdmin(admin.ModelAdmin):
    model = Cart
    list_display = ('user','cart_amount', 'cart_quantity', 'cart_nr_products', 'cart_latest_update', 'status')
    inlines = [Cart_Products]    


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)