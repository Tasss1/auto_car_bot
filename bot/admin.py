from django.contrib import admin
from .models import Car

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'condition', 'color', 'body_type', 'price_range', 'has_image']
    list_filter = ['condition', 'color', 'body_type', 'price_range']
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'description', 'image_url']
        }),
        ('Характеристики', {
            'fields': ['condition', 'color', 'body_type', 'price_range']
        }),
    ]

    def has_image(self, obj):
        return bool(obj.image_url)

    has_image.boolean = True
    has_image.short_description = 'Есть фото'