from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('MYCV.views',
    # Examples:
    url(r'^$', 'home', name='home'),
)
urlpatterns += patterns('django.contrib.auth.views',
    # login
    url(r'^accounts/login/$', 'login' ),
    url(r'^accounts/logout/$', 'logout', {'next_page':'/'} ),
)
urlpatterns += patterns('MYCV.credentials.views',
    # credentials app
    url(r'^credentials/request/$', 'request_credentials', 
            {   'redirect_ok':'/credentials/request/completed/',
                'redirect_fail':'/credentials/request/failed/'
            }),
    url(r'^credentials/request/completed/$', 'request_credentials_completed'),
    url(r'^credentials/request/failed/$', 'request_credentials_failed'),
)
urlpatterns += patterns('MYCV.credentials.views_admin',
    # credentials admin
    url(r'^(credentials/handle/)$', 'handle_pending_credentials'),
    url(r'^(credentials/handle/)(\d+)/$', 'handle_pending_credentials_request'),
    url(r'^(credentials/handle/)(\d+)/accept/$', 'accept_request'),
    url(r'^(credentials/handle/)(\d+)/reject/$', 'reject_request'),
    url(r'^(credentials/handle/)(\d+)/sent/$', 'sent_request'),
    url(r'^(credentials/handle/)(\d+)/reset/$', 'reset_request'),
    url(r'^credentials/generate_password/(\d+)/$', 'generate_password'),
)
urlpatterns += patterns('',    
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += patterns('MYCV.content.views',    
    # This is the catch-all at the end for generic content 
    #  A generic view takes care, and in the table Contents (content.models.Content) 
    #   we store the needed info: path (url), template, html content (optional), groups with permission to view
    url(r'^(.*)/$', 'view_content'),
)


# Serve MEDIA in DEV environment (uploaded files) 
# TODO - Check this way of serving static files --> changes in Django 1.4
from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
                'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT,
                 'show_indexes' : False }
            )
        )


