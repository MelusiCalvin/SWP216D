# ride2school/context_processors.py
from ride2school import settings

def google_maps_api_key(request):
    return {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}