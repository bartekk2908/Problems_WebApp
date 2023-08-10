from django import forms


class Q_Form(forms.Form):
    data = forms.CharField(label="", max_length=100)


class S_edit_Form(forms.Form):
     data = forms.CharField(label="", max_length=100)


class P_Form(forms.Form):
    pdata = forms.CharField(label="Treść problemu", max_length=100)
    sdata = forms.CharField(label="Rozwiązanie", max_length=100)
