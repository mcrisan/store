import datetime
import ipdb

from django.db import models
from django.db.models import Sum, Max, Avg, Min, Count
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxLengthValidator

from store.site_settings import SiteSettings
from .choices import s, get_field_choices

options = SiteSettings('Site Settings')
STATUS_CHOICES = (
    ('0', 'Active'),
    ('1', 'Ordered'),
)
discount_status={"active" : 0, "pending" : 1, "finished" : 2}
ACTIVE = 0
PENDING = 1
FINISHED = 2

DISCOUNT_STATUS_CHOICES = (
    ('0', 'Active'),
    ('1', 'Pending'),
    ('2', 'Finished'),
)


class UserMethods(User):
    
    def orders(self):
        orders = self.cart_set.filter(status='1').all()
        return orders
    
    def money_spent(self):
        money_spent = self.cart_set.filter(status='1').aggregate(total=Sum('cart_products__price'))
        if money_spent['total']:
            return money_spent['total']
        else:
            return 0.0
    
    def products_ordered(self):
        products_ordered = (self.cart_set.filter(status='1') 
                                         .aggregate(total=Sum('cart_products__quantity')))
        if products_ordered['total']:
            return products_ordered['total']
        else:
            return 0
        
    def latest_order(self):
        latest_order = (self.cart_set.filter(status='1') 
                                     .aggregate(latest=Max('cart_products__date_added')))
        if latest_order['latest']:
            return latest_order['latest']
        else:
            return "Not Ordered" 
        
    def first_order(self):
        first_order = (self.cart_set.filter(status='1') 
                                    .aggregate(latest=Min('cart_products__date_added')))
        if first_order['latest']:
            return first_order['latest']
        else:
            return "Not Ordered" 
        
    def offers_claimed(self):
        offers = (self.cart_set.filter(status='1', 
                                      discountedproducts__quantity__gt =0) 
                               .annotate(dcount=Count('discountedproducts__cart')))
        return offers        
            

    class Meta:
        proxy=True
        #app_label = 'auth'


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
        avg_rate = self.rating_set.filter(product__id=self.id).aggregate(Avg('value'))
        if avg_rate['value__avg']:
            return avg_rate['value__avg']   
        else:
            return 0.0
        
    def discount(self):
        discount = self.discount_set.filter(status='0').aggregate(max_percent=Max('percent'))
        if discount:
            return discount['max_percent']
        else:
            return 0
    
    def discounted_price(self):
        discount = self.discount()
        price = self.price - self.price*discount/100
        return price


class Discount(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField(validators=[MaxLengthValidator(500)])
    percent = models.FloatField("Percent",)
    start_date = models.DateField(default=datetime.datetime.now())
    end_date = models.DateField(default=datetime.datetime.now(), null=True, blank=True)
    products = models.ManyToManyField(Product)
    status = models.CharField(max_length=1,
                              choices=get_field_choices(s),
                              default='1')
    def __unicode__(self):
        return self.name 
    
    def offer_status(self):
        if self.status == '0':
            return "Active"
        elif self.status == '1':
            return "Waiting to start"
        else:
            return "This offer expired"
      
        
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
 

class CartManager(models.Manager):
    
    @staticmethod
    def orders_total_price():
        total_price = Cart.objects.filter(status='1').aggregate(total=Sum('cart_products__price'))
        return total_price['total']
    
    @staticmethod
    def total_orders():
        total_orders = Cart.objects.filter(status='1').count()
        return total_orders
    
    @staticmethod
    def total_products_ordered():
        total_orders = (Cart.objects.filter(status='1')
                           .aggregate(total=Sum('cart_products__quantity')))
        return total_orders['total']
      
    
class Cart(models.Model):
    products = models.ManyToManyField(Product, through='Cart_Products')
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default='0')
    objects = CartManager()
    
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
               self.update_from_product_cart(prod_cart, quantity, prod.discounted_price())
               prod.modify_quantity(quantity - old_quant)
        else:
              prod_cart = self.add_product_cart(prod, quantity)
              prod.modify_quantity(quantity)
        discount = prod.discount_set.filter(status='0').last() 
        if discount:     
            DiscountedProducts.add_product(discount, prod, self, quantity)      
        return prod, prod_cart
                                            
    def add_product_cart(self, prod, quantity): 
        prod_cart = self.cart_products_set.create(product = prod, cart = self, quantity = quantity,
                                                  price = prod.discounted_price() * float(quantity),
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
    
    
class DiscountedProducts(models.Model):
     discount = models.ForeignKey(Discount)
     product = models.ForeignKey(Product)
     cart = models.ForeignKey(Cart) 
     quantity = models.IntegerField("Quantity")
     
     @staticmethod
     def add_product(discount, product, cart, quantity):
        disc_prod = DiscountedProducts.objects.filter(discount=discount, 
                                                      product=product, 
                                                      cart=cart).first()
        if not disc_prod:
            disc_prod = DiscountedProducts(discount=discount, 
                                           product=product, 
                                           cart=cart, 
                                           quantity=quantity)
            disc_prod.save()
        else:
            disc_prod.quantity = quantity 
            disc_prod.save()   

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