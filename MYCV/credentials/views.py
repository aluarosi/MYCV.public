# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from forms import CredentialsRequestForm
# Local modules
from models import CredentialsRequest
# Python modules
from datetime import datetime


def request_credentials(request, redirect_ok, redirect_fail):
    if request.method == "POST":
        form = CredentialsRequestForm(data=request.POST)
        if form.is_valid():
            valid_data =  form.cleaned_data
            credential_request = CredentialsRequest(
                                    email=valid_data['email'],
                                    name=valid_data['name'],
                                    surname=valid_data['surname'],
                                    text = valid_data['message'],
                                    datetime = datetime.now() )
            credential_request.save()
            if credential_request.send_mail():
                return HttpResponseRedirect(redirect_ok) 
            else:
                return HttpResponseRedirect(redirect_fail) 
    else:
        form = CredentialsRequestForm()

    return render_to_response("credentials/request_credentials.html", 
                                context_instance = RequestContext(request),
                                dictionary = {'form': form} )

    
def request_credentials_completed(request):
    #TODO: try to determine if the request came from the request credential page??
    return render_to_response("credentials/request_credentials_completed.html", 
                                context_instance = RequestContext(request),)
    

def request_credentials_failed(request):
    #TODO: try to determine if the request came from the request credential page??
    return render_to_response("credentials/request_credentials_failed.html", 
                                context_instance = RequestContext(request),)
    
