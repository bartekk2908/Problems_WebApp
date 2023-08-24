from django import forms
from ckeditor import fields


class Q_Form(forms.Form):
    data = forms.CharField(label="", max_length=200,
                           widget=forms.TextInput(attrs={"placeholder": " wpisz frazę",
                                                         "class": "input-query"}))
    image = forms.ImageField(label="")

    def __init__(self, *args, **kwargs):
        super(Q_Form, self).__init__(*args, **kwargs)
        self.fields['data'].required = False
        self.fields['image'].required = False

    def clean(self):
        data = self.cleaned_data.get('data')
        image = self.cleaned_data.get('image')
        if not data and not image:
            raise forms.ValidationError('One of fields is required')
        return self.cleaned_data


class S_edit_Form(forms.Form):
    data = fields.RichTextFormField(label="")


class P_Form(forms.Form):
    pdata = forms.CharField(label="", max_length=200,
                            widget=forms.TextInput(attrs={"placeholder": " . . . ",
                                                          "class": "input-problem"}))
    sdata = fields.RichTextFormField(label="")


class Login_Form(forms.Form):
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)
