from django import forms

class CredentialsRequestForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField()
    surname = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

class CredentialsNoteForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea({'cols':80}))
