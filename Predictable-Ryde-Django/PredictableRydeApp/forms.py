from django import forms

class MyForm(forms.Form):
 numOfVehicles = forms.IntegerField(label='Enter the number of available vehicles')
 docFile = forms.FileField()
