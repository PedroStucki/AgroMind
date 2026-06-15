# apps/operational/urls.py  (API URLs – montado em api/v1/propriedades/<pk>/operacional/)

from django.urls import path
from . import views

app_name = "operational-api"

urlpatterns = [
    # ── Máquinas ──────────────────────────────────────────────────────────────
    path(
        "maquinas/",
        views.MaquinaListCreateView.as_view(),
        name="maquina-list",
    ),
    path(
        "maquinas/<int:maquina_id>/",
        views.MaquinaDetailView.as_view(),
        name="maquina-detail",
    ),
    path(
        "maquinas/<int:maquina_id>/historico/",
        views.MaquinaHistoricoView.as_view(),
        name="maquina-historico",
    ),

    # ── Abastecimentos ────────────────────────────────────────────────────────
    path(
        "abastecimentos/",
        views.AbastecimentoListCreateView.as_view(),
        name="abastecimento-list",
    ),
    path(
        "abastecimentos/<int:abastecimento_id>/",
        views.AbastecimentoDetailView.as_view(),
        name="abastecimento-detail",
    ),

    # ── Uso de Máquinas ───────────────────────────────────────────────────────
    path(
        "usos/",
        views.UsoMaquinaListCreateView.as_view(),
        name="uso-list",
    ),
    path(
        "usos/<int:uso_id>/",
        views.UsoMaquinaDetailView.as_view(),
        name="uso-detail",
    ),

    # ── Manutenções ───────────────────────────────────────────────────────────
    path(
        "manutencoes/",
        views.ManutencaoListCreateView.as_view(),
        name="manutencao-list",
    ),
    path(
        "manutencoes/<int:manutencao_id>/",
        views.ManutencaoDetailView.as_view(),
        name="manutencao-detail",
    ),

    # ── Programação de Manutenção ─────────────────────────────────────────────
    path(
        "programacoes/",
        views.ProgramacaoListCreateView.as_view(),
        name="programacao-list",
    ),
    path(
        "programacoes/<int:prog_id>/",
        views.ProgramacaoDetailView.as_view(),
        name="programacao-detail",
    ),
    path(
        "programacoes/<int:prog_id>/resolver/",
        views.ProgramacaoResolverView.as_view(),
        name="programacao-resolver",
    ),

    # ── Dashboards / Consolidados ─────────────────────────────────────────────
    path(
        "alertas/",
        views.AlertasManutencaoView.as_view(),
        name="alertas",
    ),
    path(
        "consolidado/",
        views.ConsolidadoCustosView.as_view(),
        name="consolidado",
    ),
]
