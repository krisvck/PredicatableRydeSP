from django import forms
from datetime import datetime

class MyForm(forms.Form):
 numOfVehicles = forms.IntegerField(label='Enter the number of available vehicles', initial=3)
 docFile = forms.FileField(label='Select CSV file in data directory')
 depotLat = forms.FloatField(label='School Latatude', initial=43.649839)
 depotLon = forms.FloatField(label='School Longitude', initial=-116.336241)
 numOfSecondsPerStop = forms.IntegerField(label='Enter the number of seconds a bus will stop at each location', initial=15)
