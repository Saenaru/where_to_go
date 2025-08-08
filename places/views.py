from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Place, Image
from django.shortcuts import render
import json

def place_details(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    
    images = Image.objects.filter(place=place).order_by('position')
    
    img_urls = []
    for img in images:
        if img.image:
            img_url = request.build_absolute_uri(img.image.url)
            img_urls.append(img_url)
        elif img.image_url:
            img_urls.append(img.image_url)
    
    response_data = {
        "title": place.title,
        "imgs": img_urls,
        "description_short": place.description_short or "",
        "description_long": place.description_long or "",
        "coordinates": {
            "lng": place.lng,
            "lat": place.lat
        }
    }
    
    return JsonResponse(
        response_data,
        json_dumps_params={'ensure_ascii': False, 'indent': 2},
        safe=False
    )

def get_places_geojson(request):
    places = Place.objects.all()
    features = []
    
    for place in places:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [place.lng, place.lat]
            },
            "properties": {
                "title": place.title,
                "placeId": f"place_{place.id}",
                "detailsUrl": f"/place/{place.id}/"
            }
        })
    
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })