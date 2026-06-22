# apps/financial/web_urls.py
from django.urls import path
from . import web_views

app_name = "web_financial"

urlpatterns = [
    path("<int:propriedade_id>/", web_views.financial_dashboard_view, name="dashboard"),
]
