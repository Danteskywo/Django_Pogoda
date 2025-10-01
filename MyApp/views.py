import os
import requests
from django.shortcuts import render
from django.http import HttpResponse
from .models import CityModel
from .forms import CityForm




# Create your views here.
def index(request):
	appid = os.environ.get('OPENWEATHER_API_KEY', '089b41837623a98e1ad261c4b10ee69b')
	# appid = os.environ['appid']
	url_template = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + appid

	if (request.method == 'POST'):
		form = CityForm(request.POST)
		if form.is_valid():
			form.save()

	form = CityForm()

	cities = CityModel.objects.all()
	all_cities = []

	for city in cities:
		res = requests.get(url_template.format(city.name)).json()
		city_info = {
			'city': city.name,
			'temp': res["main"]["temp"],
			'icon': res["weather"][0]["icon"]
		}

		all_cities.append(city_info)


	context = {'all_info': all_cities, 'form': form} 	 # Передача данных в html шаблон

	return render(request, 'index.html', context)