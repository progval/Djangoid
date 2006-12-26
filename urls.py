from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^oidserver/', include('oidserver.apps.foo.urls.foo')),
    (r'^yadis/$', 'oidserver.server.views.serveryadis'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^(?P<uid>[^/]+)/yadis/$', 'oidserver.users.views.useryadis'),
    (r'^(?P<uid>[^/]+)/$', 'oidserver.users.views.userpage'),
    (r'^$', 'oidserver.server.views.endpoint'),
)
