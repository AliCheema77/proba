from django.urls import path
from proba.views import scrap_view

app_name = 'proba'


urlpatterns = [
    path("scrap/", scrap_view, name="scrap"),
]
