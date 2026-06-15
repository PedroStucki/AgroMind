from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def home(request):
    return redirect('users:dashboard')

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),

    path("usuarios/", include("apps.users.urls", namespace="users")),
    path("propriedades/", include("apps.properties.web_urls", namespace="web_properties")),
    path("estoque/", include("apps.estoque.web_urls", namespace="web_estoque")),
    path("plantio/", include("apps.planting.web_urls", namespace="web_planting")),
    path("clima/", include("apps.weather.web_urls", namespace="web_weather")),
    path("operacional/", include("apps.operational.web_urls", namespace="web_operational")),

    path("api/propriedades/", include("apps.properties.urls", namespace="properties")),
    path("api/weather/", include("apps.weather.urls", namespace="weather")),

    # Sprint 03 — Estoque de Insumos
    path("api/v1/propriedades/<int:propriedade_id>/insumos/", include("apps.estoque.urls", namespace="estoque")),

    # Sprint 07 — Controle Operacional
    path("api/v1/propriedades/<int:propriedade_id>/operacional/", include("apps.operational.urls", namespace="operational")),

    # Safras API (consumido pelo módulo operacional e estoque)
    path("api/v1/propriedades/<int:propriedade_id>/", include("apps.planting.api_urls", namespace="planting-api")),

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]