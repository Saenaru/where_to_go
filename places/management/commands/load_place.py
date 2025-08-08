from django.core.management.base import BaseCommand
from places.models import Place, Image
import requests
from urllib.parse import urlparse
import os
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Загружает данные о месте из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('json_url', type=str, help='URL JSON-файла с данными о месте')

    def handle(self, *args, **options):
        json_url = options['json_url']
        
        try:
            response = requests.get(json_url)
            response.raise_for_status()
            place_data = response.json()
            
            # Обрабатываем как старый, так и новый формат данных
            coordinates = place_data.get('coordinates') or {}
            lng = coordinates.get('lng') or place_data.get('lng')
            lat = coordinates.get('lat') or place_data.get('lat')
            
            place, created = Place.objects.update_or_create(
                title=place_data['title'],
                defaults={
                    'description_short': place_data.get('description_short', '') or place_data.get('short_description', ''),
                    'description_long': place_data.get('description_long', '') or place_data.get('long_description', ''),
                    'lng': lng,
                    'lat': lat
                }
            )
            
            # Удаляем старые изображения только если есть новые
            if 'imgs' in place_data:
                place.images.all().delete()
                
                for position, img_url in enumerate(place_data.get('imgs', []), start=1):
                    try:
                        image = Image(place=place, position=position)
                        
                        img_response = requests.get(img_url)
                        img_response.raise_for_status()
                        
                        img_name = os.path.basename(urlparse(img_url).path)
                        
                        image.image.save(
                            img_name,
                            ContentFile(img_response.content),
                            save=True
                        )
                        self.stdout.write(f'Добавлено изображение: {img_name}')
                    except Exception as img_error:
                        self.stdout.write(self.style.WARNING(f'Ошибка загрузки изображения {img_url}: {str(img_error)}'))
                        continue
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Успешно создано новое место: {place.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Успешно обновлено место: {place.title}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при загрузке данных: {str(e)}'))
            raise e