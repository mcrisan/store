import datetime 

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Product, Category, Cart, Discount

class ProductTestCase(TestCase):
    def setUp(self):
        cat = Category.objects.create(name="animals")
        user = User.objects.create(username="marius")
        p1 = Product.objects.create(name="lion", quantity=3, price=5, category=cat, image_url="http://cdn.dice.com/wp-content/uploads/2013/06/Dice_News_Icon_04_250x200_ScreenRes.jpg")
        p2 = Product.objects.create(name="fox", quantity=30, price=50, category=cat, image_url="http://cdn.dice.com/wp-content/uploads/2013/06/Dice_News_Icon_04_250x200_ScreenRes.jpg")
        discount = Discount.objects.create(name='1', description='1',
                                   percent=20,
                                   start_date = datetime.datetime.now(),
                                   status = 0,
                                   end_date = datetime.datetime.now())
        discount.products.add(p1,p2)
        cart = Cart.objects.create(user=user, status=1)
        cart.cart_products_set.create(product = p1, cart = cart, quantity = 5,
                            price = p1.discounted_price() * float(5),
                            date_added = datetime.datetime.now(),
                            discount = discount)

    def test_modify_quantity(self):
        prod = Product.objects.get(name="lion")
        old_quantity = prod.quantity
        prod.modify_quantity(2)
        new_quantity = prod.quantity
        self.assertEqual(new_quantity, old_quantity - 2)
        
    def test_modify_quantity_to_big(self):
        prod = Product.objects.get(name="lion")
        old_quantity = prod.quantity
        prod.modify_quantity(old_quantity + 3)
        new_quantity = prod.quantity
        self.assertEqual(new_quantity, old_quantity)  
        
    def test_modify_quantity_to_small(self):
        prod = Product.objects.get(name="lion")
        old_quantity = prod.quantity
        prod.modify_quantity(-abs(old_quantity) - 3)
        new_quantity = prod.quantity
        self.assertEqual(new_quantity, old_quantity) 
        
    def test_total_orders(self):
        prod = Product.objects.get(name="lion")
        orders = prod.total_orders()
        self.assertEqual(orders, 1) 
        
    def test_quantity_ordered(self):
        prod = Product.objects.get(name="lion")
        quantity = prod.quantity_ordered()
        self.assertEqual(quantity, 5) 
        
    def test_quantity_ordered_no_orders(self):
        prod = Product.objects.get(name="fox")
        quantity = prod.quantity_ordered()
        self.assertEqual(quantity, 0) 
        
    def test_product_rating(self):
        prod = Product.objects.get(name="fox")
        rate = prod.product_rating()
        self.assertEqual(rate, 0)
        
    def test_product_discount(self):
        prod = Product.objects.get(name="fox")
        discount = prod.discount()
        self.assertEqual(discount.percent, 20)
        
    def test_product_revenue(self):
        prod = Product.objects.get(name="lion")
        revenue = prod.revenue()
        self.assertEqual(revenue, 20)
        
    def test_discounted_price(self):
        prod = Product.objects.get(name="lion")
        price = prod.discounted_price()
        self.assertEqual(price, 4)
        
    def test_is_on_wishlist(self):
        prod = Product.objects.get(name="lion")
        user = User.objects.get(username="marius")
        wishlist = prod.is_on_wishlist(user)
        self.assertEqual(wishlist, False)
        