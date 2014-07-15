import datetime
import ipdb

from django.db import models
from django.db.models import Q
from django.db.models import Sum, Max, Avg, Min, Count
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxLengthValidator
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.comments.moderation import CommentModerator, moderator

from store.site_settings import SiteSettings
from .choices import DISCOUNT_STATUS_CHOICES, CART_STATUS_CHOICES

options = SiteSettings('Site Settings')


class UserMethods(User):
    
    def orders(self):
        orders = self.cart_set.filter(status=CART_STATUS_CHOICES.ORDERED).all()
        return orders
    
    def money_spent(self):
        money_spent = (self.cart_set.filter(status=CART_STATUS_CHOICES.ORDERED)
                                    .aggregate(total=Sum('cart_products__price')))
        if money_spent['total']:
            return money_spent['total']
        else:
            return 0.0
    money_spent.admin_order_field = 'total_amount'
    
    def products_ordered(self):
        products_ordered = (self.cart_set.filter(status=CART_STATUS_CHOICES.ORDERED) 
                                         .aggregate(total=Sum('cart_products__quantity')))
        if products_ordered['total']:
            return products_ordered['total']
        else:
            return 0
    products_ordered.admin_order_field = 'nr_prod'    
        
    def latest_order(self):
        latest_order = (self.cart_set.filter(status=CART_STATUS_CHOICES.ORDERED) 
                                     .aggregate(latest=Max('cart_products__date_added')))
        if latest_order['latest']:
            return latest_order['latest']
        else:
            return "Not Ordered" 
    latest_order.admin_order_field = 'latest'     
        
    def first_order(self):
        first_order = (self.cart_set.filter(status=CART_STATUS_CHOICES.ORDERED) 
                                    .aggregate(first=Min('cart_products__date_added')))
        if first_order['first']:
            return first_order['first']
        else:
            return "Not Ordered" 
    first_order.admin_order_field = 'first' 
        
    def offers_claimed(self):
        offers = (Promotion.objects.filter(cart_products__cart__user=self).
                                   annotate(Count('id'))).count()
        return offers                   

    class Meta:
        proxy=True
        verbose_name = "User Statistics"
        verbose_name_plural = "User Statistics"


class Category(models.Model):
    name = models.CharField("Name", max_length=50)
    
    def products_category(self):
        return self.products.count()
    
    def quantity_ordered(self):
        quant = (self.products.filter(cart_products__cart__status=1).
                               aggregate(quant=Sum('cart_products__quantity'))['quant'])
        return quant
    
    def revenue(self):
        revenue = (self.products.filter(cart_products__cart__status=1).
                                 aggregate(revenue=Sum('cart_products__price'))['revenue'])
        return revenue
    
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
        discount =(self.promotion_set.filter(discount__isnull=False, status=DISCOUNT_STATUS_CHOICES.ACTIVE).
                                order_by('-percent').
                                first())
        if discount:
            return discount.discount   
        
    def promotion(self):
        prom =(self.promotion_set.filter(status=DISCOUNT_STATUS_CHOICES.ACTIVE).
                                order_by('-percent').
                                first())
        return prom       
    
    def revenue(self):
        revenue =(self.cart_products_set.filter(cart__status=CART_STATUS_CHOICES.ORDERED).
                                        aggregate(rev=Sum('price'))['rev'])
        return revenue
    
    def discounted_price(self):
        if self.discount():
            discount = self.discount().percent
        else:
            discount = 0    
        price = self.price - self.price*discount/100
        return price
        
    def has_coupon(self,code):
        promotion = self.promotion_set.filter(coupon__isnull=False, coupon__code=code, status=DISCOUNT_STATUS_CHOICES.ACTIVE).first()
        if promotion:
            return promotion.coupon
        

class ProductModerator(CommentModerator):
    moderate_after = 30

    def moderate(self, comment, content_object, request):
        already_moderated = super(ProductModerator,self).moderate(comment, content_object, request)
        if already_moderated:
            return True
        return True

moderator.register(Product, ProductModerator)


class Promotion(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField(validators=[MaxLengthValidator(500)])
    products = models.ManyToManyField(Product)
    percent = models.FloatField("Percent",)
    start_date = models.DateField(default=datetime.datetime.now())
    status = models.CharField(max_length=1,
                              choices=DISCOUNT_STATUS_CHOICES.choices,
                              default=DISCOUNT_STATUS_CHOICES.PENDING)
    
    def __unicode__(self):
        return self.name 
    
    def offer_status(self):
        if self.status == DISCOUNT_STATUS_CHOICES.ACTIVE:
            return "Active"
        elif self.status == DISCOUNT_STATUS_CHOICES.PENDING:
            return "Waiting to start"
        else:
            return "This offer expired"
        
    def quantity_ordered(self):
        quant = self.cart_products_set.aggregate(quant=Sum('quantity'))
        return quant['quant']
    
    def money_spent(self):
        price = self.cart_products_set.aggregate(price=Sum('price'))
        return price['price']
    
    def real_value(self):
        price =(self.cart_products_set.
                filter(cart__status=CART_STATUS_CHOICES.ORDERED).
                aggregate(quant=Sum('product__price', 
                                    field='webstore_cart_products.quantity*webstore_product.price'))
                ['quant'])

        return price


class Discount(Promotion):
    end_date = models.DateField(default=datetime.datetime.now(), null=True, blank=True) 

 
class Coupon(Promotion):
    code = models.CharField(max_length=20)
    volume = models.PositiveIntegerField() 
    
    def modify_quantity(self, quantity):
        self.volume -= quantity
        self.save()
   
            
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
        total_price = (Cart.objects.filter(status=CART_STATUS_CHOICES.ORDERED)
                                   .aggregate(total=Sum('cart_products__price')))
        return total_price['total']
    
    @staticmethod
    def total_orders():
        total_orders = Cart.objects.filter(status=CART_STATUS_CHOICES.ORDERED).count()
        return total_orders
    
    @staticmethod
    def total_products_ordered():
        total_orders = (Cart.objects.filter(status=CART_STATUS_CHOICES.ORDERED)
                           .aggregate(total=Sum('cart_products__quantity')))
        return total_orders['total']
      
    
class Cart(models.Model):
    products = models.ManyToManyField(Product, through='Cart_Products')
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1,
                              choices=CART_STATUS_CHOICES.choices,
                              default=CART_STATUS_CHOICES.ACTIVE)
    objects = CartManager()
    
    def __unicode__(self): 
        return self.user.username
     
    @staticmethod   
    def from_user(user):
        cart = Cart.objects.filter(user=user, status=CART_STATUS_CHOICES.ACTIVE).first()
        if not cart:
            cart = Cart(user=user)
            cart.save()         
        return cart 
        
    def check_product_cart(self, prod_id, quantity):
        prod = Product.objects.filter(id=prod_id).first()
        prod_cart = self.cart_products_set.filter(product = prod).first()
        if prod_cart:
               old_quant = prod_cart.quantity
               prod_cart.update(quantity)
               prod.modify_quantity(quantity - old_quant)
        else:
              prod_cart = self.add_product_cart(prod, quantity, prod.discount())
              prod.modify_quantity(quantity)   
        return prod, prod_cart
                                            
    def add_product_cart(self, prod, quantity, discount): 
        prod_cart = (self.cart_products_set.
                     create(product = prod, cart = self, quantity = quantity,
                            price = prod.discounted_price() * float(quantity),
                            date_added = datetime.datetime.now(),
                            discount = discount )) 
        return prod_cart
        
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
        self.status = CART_STATUS_CHOICES.ORDERED
        self.save() 
        
    def apply_discount(self, code):
        coupon = (Coupon.objects.filter(code__exact=code, 
                                        status=DISCOUNT_STATUS_CHOICES.ACTIVE).
                                 first())
        for prod in self.cart_products_set.exclude(discount = coupon):
            prod.remove_coupon()
            prod.save_coupon(code)
                
    def real_value(self): 
        price =(self.cart_products_set.
                aggregate(quant=Sum('product__price', 
                                    field='webstore_cart_products.quantity*webstore_product.price'))
                ['quant'])

        return price   
    
    def money_saved(self): 
        price =self.real_value() - self.cart_amount()
        return price 
    
    def total_discount(self):
        discount = self.money_saved()/self.real_value()*100
        return discount    
            
class Cart_Products(models.Model):
    product = models.ForeignKey(Product)
    cart = models.ForeignKey(Cart)
    quantity = models.IntegerField()
    price = models.FloatField()
    date_added = models.DateField()
    discount = models.ForeignKey(Promotion, null=True, blank=True, default = None)
    
    class Meta:
        verbose_name = "product in cart"
        
    def update(self, quantity):
        old_quant = self.quantity 
        self.quantity = quantity
        self.price = self.product.discounted_price() * float(quantity)
        self.discount = self.product.discount()
        self.save()   
        
    def remove_coupon(self):
        if self.discount and hasattr(self.discount, 'coupon'):
            self.discount.coupon.volume += self.quantity
            self.discount.coupon.save()
            self.price = self.product.discounted_price() * self.quantity
            self.discount = self.product.discount()
            self.save()
            
    def save_coupon(self, code):
        coup = self.product.has_coupon(code)
        if coup and self.quantity <= coup.volume:
            self.price = (self.product.price - self.product.price * coup.percent/100) * self.quantity
            self.discount = coup
            self.save()  
            coup.modify_quantity(self.quantity)                     
                

class DeliveryDetails(models.Model):
    address = models.CharField("Name", max_length=100)
    phonenumber = PhoneNumberField()
    user = models.ForeignKey(User)
    cart = models.ForeignKey(Cart)

    def __unicode__(self):
        return self.address
    
    @staticmethod
    def from_user(user):
        cart = user.cart_set.filter(status=CART_STATUS_CHOICES.ACTIVE).first()
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