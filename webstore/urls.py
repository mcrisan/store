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
    url(r'^notification', views.notifications, name='notifications'),
    url(r'^category/(?P<name>\w+)/$', views.products_categories, name='category'),
    url(r'^category/(?P<name>\w+)/page(?P<page>[0-9]+)/$', views.products_categories, name='category_pag'),
    url(r'^add_wishlist/(?P<prod_id>\d+)/$', views.add_to_wishlist, name='add_to_wishlist'),
    url(r'^remove_wishlist/(?P<prod_id>\d+)/$', views.remove_from_wishlist, name='remove_from_wishlist'),
    url(r'^wishlist_products/$', views.wishlist_products, name='wishlist_products'),
    url(r'^wishlist_products/page(?P<page>[0-9]+)/$', views.wishlist_products, name='wishlist_products_pag'),
    url(r'^remove_coupon', views.remove_coupon, name='remove_coupon'),
    url(r'^apply_coupon', views.apply_coupon, name='apply_coupon'),
)
