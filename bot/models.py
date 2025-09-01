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
    price = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField()

    # Фото (до 5)
    image_url1 = models.URLField('Фото 1', blank=True, null=True)
    image_url2 = models.URLField('Фото 2', blank=True, null=True)
    image_url3 = models.URLField('Фото 3', blank=True, null=True)
    image_url4 = models.URLField('Фото 4', blank=True, null=True)
    image_url5 = models.URLField('Фото 5', blank=True, null=True)

    # Видео
    video_url = models.URLField('Видео', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_condition_display()} - {self.price}$)"

    def get_all_images(self):
        """Вернуть список всех фото"""
        return [url for url in [
            self.image_url1, self.image_url2,
            self.image_url3, self.image_url4,
            self.image_url5
        ] if url]
