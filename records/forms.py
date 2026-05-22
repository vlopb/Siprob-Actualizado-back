# forms.py
from django import forms

class RecordsAdvancedSearchForm(forms.Form):
    name = forms.CharField(label='name', required=False)
    fathers_name = forms.CharField(label='fathers_name', required=False)
    mothers_name = forms.CharField(label='mothers_name', required=False)
    nickname = forms.CharField(label='nickname', required=False)
    gender = forms.CharField(label='gender', required=False)
    entry_date = forms.DateField(label='entry_date', required=False)
    qualification_release_date = forms.DateField(label='qualification_release_date', required=False)
    process = forms.CharField(label='process', required=False)
    fault = forms.CharField(label='fault', required=False)
    crime = forms.CharField(label='crime', required=False)