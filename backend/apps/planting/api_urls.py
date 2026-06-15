# apps/planting/api_urls.py
from django.urls import path
from . import api_views

app_name = "planting-api"

urlpatterns = [
    path("safras/", api_views.SafraListView.as_view(), name="safra-list"),
]
