from django.contrib import admin
from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'condition', 'color', 'body_type', 'price', 'has_media']
    list_filter = ['condition', 'color', 'body_type', 'price']
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'description']
        }),
        ('Медиа', {
            'fields': ['image_url1', 'image_url2', 'image_url3', 'image_url4', 'image_url5', 'video_url']
        }),
        ('Характеристики', {
            'fields': ['condition', 'color', 'body_type', 'price']
        }),
    ]

    def has_media(self, obj):
        return bool(obj.get_all_images() or obj.video_url)

    has_media.boolean = True
    has_media.short_description = 'Есть фото/видео'
