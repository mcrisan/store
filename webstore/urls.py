from django.conf.urls import patterns, include, url

from webstore import views

urlpatterns = patterns('',
    url(r'^addtocart', views.create_cart, name='add_cart'),
    url(r'^checkout', views.checkout, name='checkout'),
    url(r'^delete/(?P<prod_id>\d+)/$', views.delete_prod, name='delete_prod'),
    url(r'^orders', views.user_orders, name='orders'),
    url(r'^order_details/(?P<cart_id>\d+)/$', views.order_details, name='order_details'),
    url(r'^product_details/(?P<prod_id>\d+)/$', views.product_details, name='product_details'),
    url(r'^rate', views.rate_product, name='rate_product'),
    url(r'^product_rating', views.product_rating, name='product_rating'),
)
