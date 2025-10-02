import requests
from django.shortcuts import render
from django.http import HttpResponse
from .models import CityModel
from .forms import CityForm



# Create your views here.
def index(request):
	appid = '089b41837623a98e1ad261c4b10ee69b'
	# appid = os.environ['appid']
	url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + appid

	if (request.method == 'POST'):
		form = CityForm(request.POST)
		if form.is_valid():
			form.save()

	form = CityForm()

	cities = CityModel.objects.all()
	all_cities = []

	for city in cities:
		res = requests.get(url.format(city.name)).json()
		if res.get('cod') == 200:
			city_info = {
				'city': city.name,
				'temp': res["main"]["temp"],
				'icon': res["weather"][0]["icon"],
			}
		else:
        # В случае ошибки можно указать, что данные недоступны
			city_info = {
				'city': city.name,
				'temp': 'N/A',
				'icon': 'error_icon.png',  # или оставить пустым
				'error_message': res.get('message', 'Не удается получить погоду')
			}
	all_cities.append(city_info)


	context = {'all_info': all_cities, 'form': form} 	 # Передача данных в html шаблон

	return render(request, 'index.html', context)