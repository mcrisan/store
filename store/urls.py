from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'webstore.views.home', name='store_home'),
    url(r'^register', 'webstore.views.register', name='register'),
    #url(r'^$', include('webstore.urls')),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^main/', include('webstore.urls')),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    
    url(r'^login/$', 'login',
        {'template_name': 'login.html'},
        name='store_login'),
    
    url(r'^logout/$', 'logout',
        {'next_page': 'store_home'},
        name='store_logout'),  
)
