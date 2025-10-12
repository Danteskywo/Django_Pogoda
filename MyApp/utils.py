from django.utils import timezone
from .models import UserAction

def save_user_action(request, button_name):
    ip = get_client_ip(request)

    UserAction.objects.create(
        button_name = button_name,
        page_url = request.path,
        click_time = timezone.now(),
        ip_address = ip
    )

    print(f'Сохранено: {button_name} от IP {ip}')

def get_client_ip(request):
    x_forwarder_for = request.META.get('HTTP_X_FORWARDER_FOR')

    if x_forwarder_for:
        ip = x_forwarder_for.split(',')[0]

    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
