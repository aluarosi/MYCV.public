from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group

# TODO: probably this should be put in a utils file
def user_in_invitados(user):
    try:
        user.groups.get(name="invitados")
        return True
    except Exception as e:
        return False

def home(request):
    return render_to_response(  "home.html",
                                context_instance= RequestContext(request), 
                                )

@login_required
@user_passes_test(user_in_invitados, login_url="/")
def education(request):
    return render_to_response(  "pages/page_education.html",
                                context_instance= RequestContext(request), 
                                )
@login_required
@user_passes_test(user_in_invitados, login_url="/")
def photography(request):
    return render_to_response(  "pages/page_photography.html",
                                context_instance= RequestContext(request), 
                                )
@login_required
@user_passes_test(user_in_invitados, login_url="/")
def photography_perseo(request):
    return render_to_response(  "pages/page_photography_perseo.html",
                                context_instance= RequestContext(request), 
                                )
@login_required
@user_passes_test(user_in_invitados, login_url="/")
def photography_galiano(request):
    return render_to_response(  "pages/page_photography_galiano.html",
                                context_instance= RequestContext(request), 
                                )
@login_required
@user_passes_test(user_in_invitados, login_url="/")
def coding(request):
    return render_to_response(  "pages/page_coding.html",
                                context_instance= RequestContext(request), 
                                )
@login_required
@user_passes_test(user_in_invitados, login_url="/")
def music(request):
    return render_to_response(  "pages/page_music.html",
                                context_instance= RequestContext(request), 
                                )
