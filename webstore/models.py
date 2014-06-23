import datetime
import ipdb

from django.db import models
from django.db.models import Sum, Max, Avg
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from phonenumber_field.modelfields import PhoneNumberField

from store.site_settings import SiteSettings

options = SiteSettings('Site Settings')
STATUS_CHOICES = (
    ('0', 'Active'),
    ('1', 'Ordered'),
)


class Category(models.Model):
    name = models.CharField("Name", max_length=50)
    
    def __unicode__(self):  
        return self.name
       
        
class Product(models.Model):
    name = models.CharField("Name", max_length=100)
    quantity = models.IntegerField("Quantity",)
    price = models.FloatField("Price",)
    category = models.ForeignKey(Category, related_name ='products')
    image_url = models.URLField("Image URL")

    def __unicode__(self):
        return self.name
        
    def modify_quantity(self, quantity): 
        self.quantity=self.quantity - quantity   
        self.save()
        
    def total_orders(self):
        orders = self.cart_products_set.count()
        return orders 
    
    def quantity_ordered(self):
        quant = self.cart_products_set.aggregate(Sum('quantity'))
        if quant['quantity__sum']:
            return quant['quantity__sum']   
        else:
            return 0
        
    def product_rating(self):
        avg_rate = self.rating_set.filter(product__id=self.id).all().aggregate(Avg('value'))
        if avg_rate['value__avg']:
            return avg_rate['value__avg']   
        else:
            return 0.0
                
        
class Rating(models.Model):
    value = models.IntegerField("Value",)
    product = models.ForeignKey(Product)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.value  
    
    @staticmethod 
    def create_rate(user, prod_id, value):
        rate = Rating.objects.filter(user=user, product__id=prod_id).first()
        if rate:
            rate.value = value
        else:    
            product = Product.objects.get(pk=prod_id)
            rate = Rating(user=user, product=product, value=value) 
        return rate   
    
    @staticmethod 
    def from_product(prod_id):
        avg_rate = Rating.objects.filter(product__id=prod_id).all().aggregate(Avg('value'))
        return avg_rate['value__avg']     
        
    
class Cart(models.Model):
    products = models.ManyToManyField(Product, through='Cart_Products')
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default='0')
    
    def __unicode__(self): 
        return self.user.username
     
    @staticmethod   
    def from_user(user):
        cart = Cart.objects.filter(user=user, status='0').first()
        if not cart:
            cart = Cart(user=user)
            cart.save()         
        return cart 
        
    def check_product_cart(self, prod_id, quantity):
        prod = Product.objects.filter(id=prod_id).first()
        prod_cart = self.cart_products_set.filter(product = prod).first()
        if prod_cart:
               old_quant = prod_cart.quantity
               self.update_from_product_cart(prod_cart, quantity, prod.price)
               prod.modify_quantity(quantity - old_quant)
        else:
              prod_cart = self.add_product_cart(prod, quantity)
              prod.modify_quantity(quantity)
        return prod, prod_cart
                                            
    def add_product_cart(self, prod, quantity): 
        prod_cart = self.cart_products_set.create(product = prod, cart = self, quantity = quantity,
                                                  price = prod.price * float(quantity),
                                                  date_added = datetime.datetime.now() ) 
        return prod_cart
        
    @staticmethod     
    def update_from_product_cart(prod_cart, quantity, price): 
        prod_cart.quantity = quantity
        prod_cart.price = price * float(quantity)
        prod_cart.save()
        
    def cart_amount(self):
        price = self.cart_products_set.aggregate(Sum('price'))
        return price['price__sum']  
    
    def cart_quantity(self):
        quant = self.cart_products_set.aggregate(Sum('quantity'))
        return quant['quantity__sum'] 
    
    def cart_nr_products(self):
        nr_prod = self.cart_products_set.count()
        return nr_prod
    
    def cart_latest_update(self):
        date_created = self.cart_products_set.aggregate(Max('date_added'))
        return date_created['date_added__max'] 
    
    def create_order(self):
        #cart =Cart.objects.filter(user=current_user, status='0').first()
        self.status = '1'
        self.save() 
                      
            
class Cart_Products(models.Model):
    product = models.ForeignKey(Product)
    cart = models.ForeignKey(Cart)
    quantity = models.IntegerField()
    price = models.FloatField()
    date_added = models.DateField()
    
    class Meta:
        verbose_name = "product in cart"


class DeliveryDetails(models.Model):
    address = models.CharField("Name", max_length=100)
    phonenumber = PhoneNumberField()
    user = models.ForeignKey(User)
    cart = models.ForeignKey(Cart)

    def __unicode__(self):
        return self.address
    
    @staticmethod
    def from_user(user):
        cart = user.cart_set.filter(status='0').first()
        instance = DeliveryDetails.objects.filter(user=user, cart=cart).first()
        if not instance:
            instance = DeliveryDetails(user=user, cart=cart)
        return instance  
    
    @classmethod
    def latest_delivery_from_user(self, user):
        delivery = self.objects.filter(user=user).last()
        if delivery:
            details = {'address':delivery.address , 'phonenumber':delivery.phonenumber}  
        else:
            details = {'address': "" , 'phonenumber':""} 
        return details       