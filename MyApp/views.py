import requests
import json
from django.http import JsonResponse
from .models import UserAction, CityModel, ClickStats
from django.shortcuts import render
from .forms import CityForm
from django.utils import timezone

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') # Это заголовок, который используется для определения оригинального IP-адреса клиента, когда запрос проходит через прокси-серверы или балансировщики нагрузки. 
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0] # разбивает строку по запятым, образуя список.
    else:
        ip = request.META.get('REMOTE_ADDR') # Заголовок у атрибута META у обязательного параметра функции представления которая получает IP - адрес клиента.
    return ip

def save_button_click(request, button_name, page_url=None):
    if not page_url:
        page_url = request.path
    
    UserAction.objects.create(
        button_name=button_name,
        page_url=page_url,
        ip_address=get_client_ip(request),
        click_time=timezone.now()
    )

def index(request):
    appid = '089b41837623a98e1ad261c4b10ee69b'
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + appid
    
    all_cities = []
    form = CityForm()

    # Сохраняем действие при загрузке главной страницы
    save_button_click(request, 'Загрузка главной страницы', '/')

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.save(commit=False)
            # Сохраняем действие добавления города
            save_button_click(request, f'Добавление города: {new_city.name}', '/')
            new_city.save()

    cities = CityModel.objects.all()

    for city in cities:
        try:
            res = requests.get(url.format(city.name)).json()
            if res.get('cod') == 200:
                city_info = {
                    'city': city.name,
                    'temp': res["main"]["temp"],
                    'icon': res["weather"][0]["icon"],
                    'id': city.id  # Добавляем ID для отслеживания кликов
                }
            else:
                city_info = {
                    'city': city.name,
                    'temp': 'N/A',
                    'icon': 'error_icon.png',
                    'error_message': res.get('message', 'Не удается получить погоду'),
                    'id': city.id
                }
        except Exception as e:
            city_info = {
                'city': city.name,
                'temp': 'N/A',
                'icon': 'error_icon.png',
                'error_message': f'Ошибка запроса: {str(e)}',
                'id': city.id
            }
        
        all_cities.append(city_info)

    context = {'all_info': all_cities, 'form': form}
    return render(request, 'index.html', context)

def track_click(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product_name = data.get('product_name')
            button_name = data.get('button_name')
            
            # Если это клик на продукт (город)
            if product_id and product_name:
                # Сохраняем в ClickStats
                product_stats, created = ClickStats.objects.get_or_create(
                    product_id=product_id,
                    defaults={
                        'product_name': product_name, 
                        'click_count': 0,
                        'last_click': timezone.now()
                    }
                )
                
                product_stats.click_count += 1
                product_stats.last_click = timezone.now()
                product_stats.save()
                
                # Также сохраняем в UserAction
                save_button_click(request, f'Клик на город: {product_name}')
                
                response = JsonResponse({'status': 'success'})
                response.set_cookie('last_viewed_product', product_name, max_age=3600*24*7)
                response.set_cookie('last_viewed_product_id', product_id, max_age=3600*24*7)
                return response
            
            # Если это клик на обычную кнопку
            elif button_name:
                save_button_click(request, button_name)
                return JsonResponse({'status': 'success', 'message': 'Действие сохранено'})
                
            return JsonResponse({'error': 'Недостаточно данных'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'})
        except Exception as e:
            return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'})
    
    return JsonResponse({'error': 'Запрос должен быть в формате POST'})

def stats_page(request):
    # Сохраняем действие просмотра статистики
    save_button_click(request, 'Просмотр статистики', '/stats/')
    
    # Получаем статистику кликов по продуктам
    click_stats = ClickStats.objects.all().order_by('-click_count')
    
    # Статистика по кнопкам из UserAction
    from django.db.models import Count
    button_stats = UserAction.objects.values('button_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Последние действия
    recent_actions = UserAction.objects.all().order_by('-click_time')[:20]
    
    # Общая статистика
    total_clicks = sum(stat.click_count for stat in click_stats)
    total_actions = UserAction.objects.count()
    most_popular = click_stats.first() if click_stats else None
    
    context = {
        'click_stats': click_stats,
        'total_clicks': total_clicks,
        'total_actions': total_actions,
        'most_popular': most_popular,
        'button_stats': button_stats,
        'recent_actions': recent_actions,
    }
    
    return render(request, 'stats.html', context)