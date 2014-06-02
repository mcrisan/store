from django.contrib import admin

from webstore.models import Category
from webstore.models import Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    
    list_display = ('name', )
    #list_filter = ['pub_date']
    search_fields = ['name']

    inlines = [ProductInline]

admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    
    list_display = ('name', 'quantity', 'price')
    #list_filter = ['pub_date']
    search_fields = ['name']

   



admin.site.register(Product, ProductAdmin)