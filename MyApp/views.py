from django.shortcuts import render
from django.http import HttpResponse
from .models import CityModel
from .forms import CityForm



# Create your views here.
def index(request):
    if (request.metho == "POST"):
        form = CityForm(request.POST)
        form.save()

    form = 
    return render (request, 'index.html')