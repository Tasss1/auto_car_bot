import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_bot.settings')
django.setup()

from bot.models import Car

# Очистите старые данные (осторожно!)
Car.objects.all().delete()

# Добавьте тестовые машины
test_cars = [
    {'name': 'Kia Rio', 'condition': 'new', 'color': 'red', 'body_type': 'sedan', 'price_range': '5000$ - 10000$', 'description': 'Тестовая машина 1'},
    {'name': 'Hyundai Solaris', 'condition': 'new', 'color': 'black', 'body_type': 'sedan', 'price_range': '5000$ - 10000$', 'description': 'Тестовая машина 2'},
    {'name': 'Toyota Camry', 'condition': 'used', 'color': 'blue', 'body_type': 'suv', 'price_range': '10000$ - 15000$', 'description': 'Тестовая машина 3'},
]

for car_data in test_cars:
    Car.objects.create(**car_data)

print("✅ Тестовые машины добавлены!")