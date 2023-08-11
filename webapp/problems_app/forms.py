from django import forms
from ckeditor import fields


class Q_Form(forms.Form):
    data = forms.CharField(label="", max_length=200,
                           widget=forms.TextInput(attrs={"placeholder": " . . . ",
                                                         "class": "input-query"}))


class S_edit_Form(forms.Form):
     data = fields.RichTextFormField(label="Rozwiązanie")


class P_Form(forms.Form):
    pdata = forms.CharField(label="Treść problemu", max_length=200,
                            widget=forms.TextInput(attrs={"placeholder": " . . . ",
                                                          "class": "input-problem"}))
    sdata = fields.RichTextFormField(label="Rozwiązanie")
