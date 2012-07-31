from django import forms

class UrlForm(forms.Form):
    url = forms.URLField(label='craigslist page to phototize', required=True)
