from django.conf.urls import patterns, include, url
from view import home
from apis import writePost

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bigboard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/$',home)
    #url(r'^api/writePost/$',writePost)
)
