import os

from django.shortcuts import render
import random
from .forms import UploadForm
from .functions import process_py
from django.shortcuts import render
import csv

# Gender Model
random.seed(42)

# file paths
py_file = "render/static/render/python_file.py"
py_responses = "render/static/render/pyfile_responses.csv"


def index(request):
    if request.method == 'POST':
        # create an instance of our form, and fill it with the POST data
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            pyfile = request.FILES.get('file')

            upload_obj = form.save()

            # TODO: add gender classification etc to sql data base
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            github = form.cleaned_data['github']
            # upload = form.cleaned_data['upload']

            python_file = open(py_file, "w")
            python_file.write(pyfile.read().decode())
            python_file.close()

            # Process the Python file
            processed_results = process_py(py_file)

            form.pylint_score = processed_results['pylint_score']

            file = open(py_responses, 'a')
            writer = csv.writer(file)
            writer.writerow([name, email, github,
                             processed_results['pylint_score'],
                             processed_results['output_gender_guess'],
                             processed_results['output_gender_proba']])
            file.close()

            return render(request, 'render/results.html',
                          {'pylint_score': processed_results['pylint_score'],
                           'output_gender_guess': processed_results['output_gender_guess'],
                           'output_gender_proba': processed_results['output_gender_proba'],
                           'feature_importance': processed_results['feature_importance']})

    else:
        # this must be a GET request, so create an empty form
        form = UploadForm()

    return render(request, 'render/index.html', {'form': form})
