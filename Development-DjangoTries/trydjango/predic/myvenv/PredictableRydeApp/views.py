
from django.shortcuts import render
from PredictableRydeApp.forms import MyForm
from django.template import loader
from django.http import HttpResponse
import subprocess
from subprocess import Popen, PIPE, STDOUT
import os

def PredictableRydeform(request):
 #if form is submitted
     if request.method == 'POST':
        myForm = MyForm(request.POST, request.FILES)

        if myForm.is_valid():
            numOfVehicles = myForm.cleaned_data['numOfVehicles']
            docFile = myForm.cleaned_data['docFile']

            # Output is printed results of running generateRoute.py
            output = subprocess.check_output(["python","generateRoute.py", str(numOfVehicles), str(docFile.name)])
            output = output.decode("utf-8")
            context = {
            'numOfVehicles': numOfVehicles,
            'docFile': docFile,
            'output': output
            }

            template = loader.get_template('results.html')

            return HttpResponse(template.render(context, request))
     else:
         form = MyForm()

     return render(request, 'PredictableRyde.html', {'form':form});
