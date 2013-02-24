# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
# Local modules
from models import CredentialsRequest
from models import CredentialsNote
from forms import CredentialsNoteForm
# Python modules
from datetime import datetime

@user_passes_test(lambda u: u.is_superuser)
def handle_pending_credentials(request, url):
    """ Admin page for dispatching pending credentials requests"""
    states = [ i[0] for i in CredentialsRequest.STATES ]

    selected_state = request.GET.get('stateselector','ALL')
    if selected_state in states:
        filtered_credentials = CredentialsRequest.objects.filter(state=selected_state)
    else:
        filtered_credentials = CredentialsRequest.objects.all()

    return render_to_response("credentials/handle_credentials.html", 
                                context_instance = RequestContext(request),
                                dictionary= {   'filtered_credentials':filtered_credentials, 
                                                'url': url,
                                                'states': states,
                                                'selected_state':selected_state,
                                            }
                            )

@user_passes_test(lambda u: u.is_superuser)
def handle_pending_credentials_request(request, url, id):
    """ Admin page for dispatching a single credential request"""
    try:
        credential_request = CredentialsRequest.objects.get(id=id)
        credential_notes = CredentialsNote.objects.filter(credentials_request=credential_request)
    except CredentialsRequest.DoesNotExist:
        raise Http404
    else:
        if request.method == 'POST':
            form = CredentialsNoteForm(data=request.POST)
            if form.is_valid():
                valid_data = form.cleaned_data  
                new_note = CredentialsNote  (   text=valid_data['text'],
                                                time_creation=datetime.now(),
                                                user=request.user,
                                                credentials_request=credential_request,
                                            ) 
                new_note.save()
                return HttpResponseRedirect("") 
        else:
            form = CredentialsNoteForm()         
        return render_to_response   (   "credentials/handle_credential_request.html", 
                                        context_instance = RequestContext(request),
                                        dictionary= {   'credential_request':credential_request, 
                                                        'state_manager': credential_request.state_manager,  
                                                        'url': url,
                                                        'form': form, 
                                                        'notes': credential_notes,
                                                    }
                                    )

@user_passes_test(lambda u: u.is_superuser)
def accept_request(request, url, id):
    try:
        credential_request = CredentialsRequest.objects.get(id=id)
    except CredentialsRequest.DoesNotExit:
        return HttpResponseNotFound()  
    else:
        credential_request.state_manager.accept()
        return HttpResponseRedirect("/"+url+id+"/")

@user_passes_test(lambda u: u.is_superuser)
def reject_request(request, url, id):
    try:
        request = CredentialsRequest.objects.get(id=id)
    except CredentialsRequest.DoesNotExit:
        return HttpResponseNotFound()  
    else:
        request.state_manager.reject()
        return HttpResponseRedirect("/"+url+id+"/")

@user_passes_test(lambda u: u.is_superuser)
def reset_request(request, url, id):
    try:
        request = CredentialsRequest.objects.get(id=id)
    except CredentialsRequest.DoesNotExit:
        return HttpResponseNotFound()  
    else:
        request.state_manager.reset()
        return HttpResponseRedirect("/"+url+id+"/")

@user_passes_test(lambda u: u.is_superuser)
def sent_request(request, url, id):
    try:
        request = CredentialsRequest.objects.get(id=id)
    except CredentialsRequest.DoesNotExit:
        return HttpResponseNotFound()  
    else:
        request.state_manager.sent()
        return HttpResponseRedirect("/"+url+id+"/")

@user_passes_test(lambda u: u.is_superuser)
def generate_password(request, id):
    response_text = "ERROR: password generation not possible"
    try:
        credential_request = CredentialsRequest.objects.get(id=id)
    except DoesNotExist:
        # TODO: check this error handling...
        response_text = "ERROR: credential request does not exist"
    else:
        if credential_request.state_manager.is_password_generation_allowed():
            # 1st make password
            response_text = User.objects.make_random_password(length=6)
            # 2nd save it into user
            credential_request.state_manager.assign_password(response_text)
            # 3rd add note with password generation info
            print datetime.now()
            print request.user
            print credential_request
            note = CredentialsNote (    time_creation = datetime.now(),
                                        text = "Password generation: [%s]" % response_text,
                                        user = request.user,
                                        credentials_request = credential_request
                                    )
            note.save() 
            # TODO: previous steps should be included in model?
    return HttpResponse(response_text)
