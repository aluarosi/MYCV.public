from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.base import TemplateDoesNotExist
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import redirect_to_login

from models import Content

#TODO: check access permission (group based)

# Decorator
def check_permission(view):
    def view_decorated(request, url):
        try:
            content = Content.objects.get(path=url) 
        except Content.DoesNotExist:
            raise Http404
        if content.public:
            # This is when content is flagged as "public"
            return view(request, url)
        groups_of_user = set(request.user.groups.all())
        groups_of_content = set(content.allowed_groups.all())
        if groups_of_user.intersection(groups_of_content) or request.user.is_superuser:
            return view(request, url)
        else:
            #TODO: review this as in django.contrib.auth.decorators
            return redirect_to_login(request.get_full_path())
    return view_decorated


@check_permission
def view_content(request, url):
    try:
        # TODO: this should be cached, we've queried the database in the decorator
        content = Content.objects.get(path=url)
    except Content.DoesNotExist:
        raise Http404 
    else:
        template = content.template
        if not template:
            template = "%s.html" % content.path
        html_content = content.html_content
        try:
            return render_to_response(  template,
                                    context_instance= RequestContext(request), 
                                    dictionary = {'html_content' : html_content }
                                 )
        except TemplateDoesNotExist:
            raise Http404
             
