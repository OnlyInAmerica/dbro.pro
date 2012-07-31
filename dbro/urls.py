from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from blog.feeds import LatestEntriesFeed


urlpatterns = patterns('',
    # Home
    url(r'^$', 'blog.views.home', name='home'),

    # Read Post
    url(r'^read/(?P<slug>[-\w]+)', 'blog.views.article', name='article'),

    # Filter
    url(r'^filter/(?P<cat>\w+)$', 'blog.views.filter'),

    # Blog RSS
    url(r'^feed/$', LatestEntriesFeed()),
    #url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
    #{'feed_dict': feeds}),

    # CraigPhoto!
    url(r'^photocraig', 'sandbox.views.photocraig'),

    # url(r'^dbro/', include('dbro.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
