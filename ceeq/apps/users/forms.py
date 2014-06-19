from django import forms


class UserSettingsForm(forms.Form):
    bug = forms.BooleanField()
    new_feature = forms.BooleanField()
    task = forms.BooleanField()
    improvement = forms.BooleanField()
