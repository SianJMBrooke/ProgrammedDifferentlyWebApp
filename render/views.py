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

            python_file = open(py_file, "w")
            python_file.write(pyfile.read().decode())
            python_file.close()

            # Process the Python file
            processed_results = process_py(py_file)

            form.pylint_score = processed_results['pylint_score']
            form.gender_guess = processed_results['output_gender_guess']
            form.feature_importance = processed_results['feature_importance']

            return render(request, 'render/results.html',
                          {'pylint_score': processed_results['pylint_score'],
                           'output_gender_guess': processed_results['output_gender_guess'],
                           'output_gender_proba': processed_results['output_gender_proba'],
                           'feature_importance': processed_results['feature_importance']})

    else:
        # this must be a GET request, so create an empty form
        form = UploadForm()

    return render(request, 'render/index.html', {'form': form})
