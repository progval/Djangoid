from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^djangoid/', include('djangoid.apps.foo.urls.foo')),
    (r'^yadis/$', 'djangoid.server.views.serveryadis'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^(?P<uid>[^/]+)/yadis/$', 'djangoid.users.views.useryadis'),
    (r'^(?P<uid>[^/]+)/$', 'djangoid.users.views.userpage'),
    (r'^$', 'djangoid.server.views.endpoint'),
)
