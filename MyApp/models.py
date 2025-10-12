from django.db import models
from django.utils import timezone

# Create your models here.

class CityModel(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length = 40, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserAction(models.Model):
    button_name = models.CharField(max_length = 100)
    page_url = models.CharField(max_length = 200)
    click_time = models.DateTimeField(default = timezone.now)
    ip_address = models.GenericIPAddressField(blank = True, null = True)

    def __str__(self):
        return f'Клик на {self.button_name} в {self.click_time}'
    

class ClickStats(models.Model):
    product_id = models.IntegerField(unique=True)
    product_name = models.CharField(max_length=255)
    click_count = models.IntegerField(default=0)
    last_click = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.product_name}: {self.click_count} кликов"
