from django.shortcuts import render
from django.http import JsonResponse
from .models import Place, Image

def places_json(request):
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

def place_details(request, place_id):
    place = Place.objects.get(id=place_id)
    images = place.images.order_by('position')
    
    return JsonResponse({
        "title": place.title,
        "imgs": [img.image.url for img in images if img.image],
        "description_short": place.description_short,
        "description_long": place.description_long,
        "coordinates": {
            "lng": place.lng,
            "lat": place.lat
        }
    })