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
from django.core.cache import cache

from store.site_settings import SiteSettings
from .choices import DISCOUNT_STATUS_CHOICES, CART_STATUS_CHOICES, USER_GENDER_CHOICES

options = SiteSettings('Site Settings')


class ProxyUser(User):
    
    def orders(self):
        orders = self.cart_set.filter(status=CART_STATUS_CHOICES.ORDERED).all()
        return orders
    
    def order(self, order_id):
        order = self.cart_set.filter(id=order_id, 
                                    status=CART_STATUS_CHOICES.ORDERED).first()
        return order
    
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
    
    def has_ordered_product(self, prod_id):
        return self.cart_set.filter(products__id=prod_id, status='1').exists() 
    
    def has_ordered(self):
        return self.cart_set.filter(status=CART_STATUS_CHOICES.ORDERED).exists()
     
    def active_cart(self):
        return self.cart_set.filter(status=CART_STATUS_CHOICES.ACTIVE).first() 
                 

    class Meta:
        proxy=True
        verbose_name = "User Statistics"
        verbose_name_plural = "User Statistics"


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    gender = models.CharField(max_length=20, null=True, blank=True,
                              choices=USER_GENDER_CHOICES.choices)
    location = models.CharField(max_length=250, null=True, blank=True)
    hometown = models.CharField(max_length=250, null=True, blank=True)
    birthday = models.DateField(blank=True, null=True)
    locale = models.CharField(max_length=10, blank=True, null=True)
    photo_url = models.URLField("Photo URL")
    
    def __unicode__(self):
        return u'%s profile' % self.user.username


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


class ProductManager(models.Manager):
    
    def number_of_orders(self):
        return self.annotate(num_orders=Count('cart_products'))
    
    def search(self, query):
        return self.filter(name__icontains=query)
       
        
class Product(models.Model):
    name = models.CharField("Name", max_length=100)
    quantity = models.IntegerField("Quantity",)
    price = models.FloatField("Price",)
    category = models.ForeignKey(Category, related_name ='products')
    image_url = models.URLField("Image URL")
    
    objects = ProductManager()

    def __unicode__(self):
        return self.name
        
    def modify_quantity(self, quantity): 
        if (self.quantity >= abs(quantity)):
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
        discount =(self.promotion_set.filter(discount__isnull=False, 
                                             status=DISCOUNT_STATUS_CHOICES.ACTIVE).
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
        promotion = self.promotion_set.filter(coupon__isnull=False, 
                                              coupon__code=code, 
                                              status=DISCOUNT_STATUS_CHOICES.ACTIVE).first()
        if promotion:
            return promotion.coupon
    
    def is_on_wishlist(self, user):
        if self.wishlist_set.filter(user=user).first():  
            return True 
        else:
            return False    
        

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


class DiscountManager(models.Manager):
    
    def active_discounts(self):
        return self.filter(status=CART_STATUS_CHOICES.ACTIVE)


class Discount(Promotion):
    end_date = models.DateField(default=datetime.datetime.now(), null=True, blank=True)   
    objects = DiscountManager() 

 
class Coupon(Promotion):
    code = models.CharField(max_length=20)
    volume = models.PositiveIntegerField() 
    first_order = models.BooleanField()
    
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
        rate.save()    
        return rate   
    
    @staticmethod 
    def from_product(prod_id):
        avg_rate = Rating.objects.filter(product__id=prod_id).all().aggregate(Avg('value'))
        return avg_rate['value__avg']     
 

class CartManager(models.Manager):
    
    def orders_total_price(self):
        total_price = (self.filter(status=CART_STATUS_CHOICES.ORDERED)
                                   .aggregate(total=Sum('cart_products__price')))
        return total_price['total']
    
    def total_orders(self):
        total_orders = self.filter(status=CART_STATUS_CHOICES.ORDERED).count()
        return total_orders
    
    def total_products_ordered(self):
        total_orders = (self.filter(status=CART_STATUS_CHOICES.ORDERED)
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
    
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('webstore:review_order')
     
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
        
    def check_coupon(self, code):
        coupon = (Coupon.objects.filter(code__exact=code, 
                                        status=DISCOUNT_STATUS_CHOICES.ACTIVE).
                                 first()) 
        if coupon and self.user.has_ordered() ==True and coupon.first_order==True:
            pass  
        else:
            return coupon 
        
    def apply_discount(self, code):
        coupon = self.check_coupon(code)
        if not coupon:
            return
        cart_has_coupon=False
        for prod in self.cart_products_set.exclude(discount = coupon):
            prod.remove_coupon()
            if prod.save_coupon(code):
                cart_has_coupon=True
        if cart_has_coupon:
            return coupon 
        
    def remove_coupon(self): 
        for prod in self.cart_products_set.exclude(discount__coupon__isnull=True):
            prod.remove_coupon()      
                
    def real_value(self): 
        price =(self.cart_products_set.
                aggregate(quant=Sum('product__price', 
                                    field='webstore_cart_products.quantity*webstore_product.price'))
                ['quant'])

        return price   
    
    def get_product(self, prod_id):
       return self.cart_products_set.filter(product__id=prod_id).first()
    
    def money_saved(self): 
        price =self.real_value() - self.cart_amount()
        return price 
    
    def total_discount(self):
        discount = self.money_saved()/self.real_value()*100
        return discount    
    
    def has_coupon(self):
        prod = self.cart_products_set.filter(discount__coupon__isnull = False).first()
        if prod:
            return prod.discount
            
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
            return True                   
                

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
    
    
class WishList(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    products = models.ManyToManyField(Product)
    date_created = models.DateField(default=datetime.datetime.now())

    def __unicode__(self):
        return self.user.username
    
    @classmethod
    def from_user(cls,user):
        try:
            wishlist = cls.objects.get(user=user)
        except cls.DoesNotExist:
            wishlist = cls(user=user)
        return wishlist
    
    def add_to_wishlist(self, product):
        if not self.products.filter(id=product.id).first():  
            self.products.add(product) 
            message ="Product was added" 
        else:
            message ="Product is already on your wishlist"
        return message 
    
    def remove_from_wishlist(self, product):
        prod = self.products.filter(id=product.id).first()
        if prod:  
            self.products.remove(product)
            message ="Product was removed"
        else:
            message ="Product was not found on your wishlist"
        return message
    
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('webstore:wishlist_products')
         