from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'webstore.views.home', name='store_home'),
    url(r'^sortbyname/(?P<type>\d+)/$', 'webstore.views.sort_by_name', name='sort_by_name'),
    url(r'^sortbypopularity/(?P<type>\d+)/$', 'webstore.views.sort_by_popularity', name='sort_by_popularity'),
    url(r'^register', 'webstore.views.register', name='register'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^store/', include('webstore.urls', namespace='webstore', app_name='webstore')),
    
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'},
        name='store_login'),   
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': 'store_home'},
        name='store_logout'),  
    
)

