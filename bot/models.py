from django.db import models


class Car(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/У')
    ]

    COLOR_CHOICES = [
        ('red', 'Красный'),
        ('black', 'Черный'),
        ('blue', 'Синий'),
        ('green', 'Зеленый'),
        ('yellow', 'Желтый')
    ]

    BODY_TYPE_CHOICES = [
        ('sedan', 'Седан'),
        ('suv', 'Внедорожник'),
        ('hatchback', 'Хэтчбек'),
        ('coupe', 'Купе'),
        ('minivan', 'Минивэн')
    ]

    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    body_type = models.CharField(max_length=15, choices=BODY_TYPE_CHOICES)
    price = models.IntegerField()  # 👈 число вместо строки
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField('Ссылка на фото', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_condition_display()} - {self.price}$)"
