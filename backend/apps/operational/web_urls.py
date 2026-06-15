# apps/operational/web_urls.py
from django.urls import path
from . import web_views

app_name = "web_operational"

urlpatterns = [
    path("", web_views.operational_select_view, name="select"),
    path("<int:propriedade_id>/", web_views.operational_dashboard_view, name="dashboard"),
]
