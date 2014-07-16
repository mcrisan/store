from django.conf.urls import patterns, include, url

from django.contrib import admin
import notifications

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'webstore.views.home', name='store_home'),
    url(r'^page(?P<page>[0-9]+)/$', 'webstore.views.home', name='store_home_pag'),
    url(r'^sortbyname/(?P<type>\w+)/$', 'webstore.views.sort_by_name', name='sort_by_name'),
    url(r'^sortbyname/(?P<type>\w+)/(?P<page>[0-9]+)/$', 'webstore.views.sort_by_name', name='sort_by_name_pag'),
    url(r'^sortbypopularity/(?P<type>\w+)/$', 'webstore.views.sort_by_popularity', name='sort_by_popularity'),
    url(r'^sortbypopularity/(?P<type>\w+)/(?P<page>[0-9]+)/$', 'webstore.views.sort_by_popularity', name='sort_by_popularity_pag'),
    url(r'^register', 'webstore.views.register', name='register'),
    url(r'^editaccount', 'webstore.views.edit_account', name='edit_account'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url('^inbox/notifications/', include(notifications.urls)),
    url(r'^createcom', 'webstore.views.comment', name='comment'),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^settings/', include('dbsettings.urls')),
    url(r'^paypal/ipn', include('paypal.standard.ipn.urls')),
    url(r'^payment/success', 'webstore.views.payment_success', name='success'),
    url(r'^payment/canceled', 'webstore.views.payment_canceled', name='canceled'),
    url(r'^store/', include('webstore.urls', namespace='webstore', app_name='webstore')),
    
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'},
        name='store_login'),   
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': 'store_home'},
        name='store_logout'),  
    
)

