from django.contrib import admin
from django.utils.html import format_html
from .models import Place, Image
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase

class ImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Image
    extra = 1
    fields = ('image_url', 'image', 'preview')
    readonly_fields = ('preview',)
    ordering = ('position',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="200" />', obj.image.url)
        return "Нет изображения"

@admin.register(Place)
class PlaceAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ('title', 'description_short')
    search_fields = ('title', 'description_short')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('place', 'position', 'preview')
    list_editable = ('position',)
    fields = ('place', 'image_url', 'image', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="200" />', obj.image.url)
        return "Нет изображения"