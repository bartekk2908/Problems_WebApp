from django import forms
from ckeditor import fields


class QFormv2(forms.Form):
    richtext = fields.RichTextFormField(label="", max_length=10_000)


class QForm(forms.Form):
    data = forms.CharField(label="", max_length=200,
                           widget=forms.TextInput(attrs={"placeholder": " wpisz frazę",
                                                         "class": "input-query"}))
    image = forms.ImageField(label="")

    def __init__(self, *args, **kwargs):
        super(QForm, self).__init__(*args, **kwargs)
        self.fields['data'].required = False
        self.fields['image'].required = False

    def clean(self):
        data = self.cleaned_data.get('data')
        image = self.cleaned_data.get('image')
        if not data and not image:
            raise forms.ValidationError('One of fields is required')
        return self.cleaned_data


class SEditForm(forms.Form):
    data = fields.RichTextFormField(label="")


class PForm(forms.Form):
    pdata = forms.CharField(label="", max_length=200,
                            widget=forms.TextInput(attrs={"placeholder": " . . . ",
                                                          "class": "input-problem"}))
    sdata = fields.RichTextFormField(label="")


class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label=" login",
                               widget=forms.TextInput(attrs={"placeholder": " ",
                                                             "class": "input-login"}))
    password = forms.CharField(max_length=63, label="hasło",
                               widget=forms.PasswordInput(attrs={"placeholder": " ",
                                                                 "class": "input-login"}))
