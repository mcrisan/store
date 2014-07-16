from django.conf.urls import patterns, include, url

from webstore import views

urlpatterns = patterns('',
    url(r'^addtocart', views.create_cart, name='add_cart'),
    url(r'^delivery_details', views.delivery_details, name='delivery_details'),
    url(r'^revieworder', views.review_order, name='review_order'),
    url(r'^checkout', views.checkout, name='checkout'),
    url(r'^delete/(?P<prod_id>\d+)/$', views.delete_prod, name='delete_prod'),
    url(r'^orders', views.user_orders, name='orders'),
    url(r'^order_details/(?P<cart_id>\d+)/$', views.order_details, name='order_details'),
    url(r'^product_details/(?P<prod_id>\d+)/$', views.product_details, name='product_details'),
    url(r'^rate', views.rate_product, name='rate_product'),
    url(r'^product_rating', views.product_rating, name='product_rating'),
    url(r'^search', views.search, name='search'),
    url(r'^search/page(?P<page>[0-9]+)/$', views.search, name='search_pag'),
    url(r'^offers', views.offers, name='offers'),
    url(r'^offer_details/(?P<offer_id>\d+)/$', views.offer_details, name='offer_details'),
    url(r'^notification', 'webstore.views.notifications', name='notifications'),
)
