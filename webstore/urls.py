from django.conf.urls import patterns, include, url

from webstore import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'store.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^home', views.home, name='home_p')
)
