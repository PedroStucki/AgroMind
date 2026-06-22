# apps/financial/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = "financial-api"

router = DefaultRouter()
router.register(r"despesas", api_views.DespesaViewSet, basename="despesa")
router.register(r"receitas", api_views.ReceitaViewSet, basename="receita")

urlpatterns = [
    # Inclui as rotas do router
    path("", include(router.urls)),
    
    # Endpoints de consulta e relatórios
    path(
        "consolidado/",
        api_views.ConsolidadoFinanceiroAPIView.as_view(),
        name="consolidado",
    ),
    path(
        "fluxo-caixa/",
        api_views.FluxoCaixaAPIView.as_view(),
        name="fluxo-caixa",
    ),
]
