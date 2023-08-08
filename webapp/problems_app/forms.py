from django import forms


class PForm(forms.Form):
    pdata = forms.CharField(label="", max_length=100)


class SForm(forms.Form):
     sdata = forms.CharField(label="", max_length=100)
