# apps/operational/tests/test_operational.py
# Python 3.12+ | Django 5.x | pytest

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.properties.models import Propriedade, Talhao
from apps.properties import services as prop_services
from apps.planting.models import Safra
from apps.operational.models import (
    Maquina, Abastecimento, UsoMaquina, Manutencao, ProgramacaoManutencao,
    CategoriaMaquina, AtividadeMaquina, TipoManutencao, CriterioProgramacao
)
from apps.operational import services, selectors

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="produtor@agro.com",
        name="Produtor Teste",
        password="Senha@1234",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="outro@agro.com",
        name="Outro User",
        password="Senha@1234",
    )


@pytest.fixture
def propriedade(db, user):
    return prop_services.create_propriedade(
        owner=user,
        nome="Fazenda Sol Nascente",
        area_total="300.00",
        municipio="Formosa",
        uf="GO",
        latitude="-15.5432",
        longitude="-47.3321",
    )


@pytest.fixture
def other_propriedade(db, other_user):
    return prop_services.create_propriedade(
        owner=other_user,
        nome="Fazenda Outro",
        area_total="100.00",
        municipio="Formosa",
        uf="GO",
        latitude="-15.5432",
        longitude="-47.3321",
    )


@pytest.fixture
def talhao(db, propriedade):
    return prop_services.create_talhao(
        propriedade=propriedade,
        nome="Gleba 1",
        area="120.00",
        tipo_solo="argiloso",
    )


@pytest.fixture
def safra(db, user, propriedade):
    return Safra.objects.create(
        owner=user,
        propriedade=propriedade,
        nome="Safra 2025/2026",
        cultura="soja",
        data_inicio="2025-10-01",
        data_fim="2026-03-31",
    )


@pytest.fixture
def maquina(db, user, propriedade):
    return services.create_maquina(
        owner=user,
        propriedade_id=propriedade.id,
        nome="Trator John Deere 6100J",
        modelo="6100J",
        categoria="trator",
        horimetro_atual=150.00,
        custo_hora=150.00,
    )


@pytest.fixture
def client_auth(user):
    client = APIClient()
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


# ── Services: Maquina ─────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_create_maquina_sucesso(user, propriedade):
    m = services.create_maquina(
        owner=user,
        propriedade_id=propriedade.id,
        nome="Colheitadeira S700",
        modelo="S700",
        categoria="colheitadeira",
        horimetro_atual=50.00,
        custo_hora=450.00,
    )
    assert m.pk is not None
    assert m.nome == "Colheitadeira S700"
    assert m.horimetro_atual == Decimal("50.00")
    assert m.is_active is True


@pytest.mark.django_db
def test_update_maquina(maquina):
    services.update_maquina(maquina=maquina, nome="Trator JD Modificado", custo_hora=180.00)
    maquina.refresh_from_db()
    assert maquina.nome == "Trator JD Modificado"
    assert maquina.custo_hora == Decimal("180.00")


@pytest.mark.django_db
def test_deactivate_maquina(maquina):
    services.deactivate_maquina(maquina)
    maquina.refresh_from_db()
    assert maquina.is_active is False


# ── Services: Abastecimento ───────────────────────────────────────────────────

@pytest.mark.django_db
def test_create_abastecimento(user, maquina, safra):
    ab = services.create_abastecimento(
        owner=user,
        maquina_id=maquina.id,
        safra_id=safra.id,
        data="2026-01-15",
        tipo_combustivel="Diesel S10",
        quantidade=100.0,
        valor_total=600.0,
    )
    assert ab.pk is not None
    assert ab.quantidade == Decimal("100.00")
    assert ab.valor_total == Decimal("600.00")

    ab2 = services.create_abastecimento(
        owner=user,
        maquina_id=maquina.id,
        safra_id=safra.id,
        data="2026-01-16",
        tipo_combustivel="Diesel S10",
        quantidade=50.0,
        valor_total=300.0,
        horimetro=165.50,
    )
    maquina.refresh_from_db()
    assert maquina.horimetro_atual == Decimal("165.50")
    assert ab2.horimetro == Decimal("165.50")

    with pytest.raises(ValidationError):
        services.create_abastecimento(
            owner=user,
            maquina_id=maquina.id,
            safra_id=safra.id,
            data="2026-01-17",
            tipo_combustivel="Diesel S10",
            quantidade=50.0,
            valor_total=300.0,
            horimetro=160.00,
        )


# ── Services: UsoMaquina ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_create_uso_maquina(user, maquina, talhao, safra):
    horimetro_inicial = maquina.horimetro_atual
    uso = services.create_uso_maquina(
        owner=user,
        maquina_id=maquina.id,
        talhao_id=talhao.id,
        safra_id=safra.id,
        data="2026-01-20",
        hora_inicio="08:00:00",
        hora_fim="12:00:00",
        horas_trabalhadas=4.50,
        atividade="plantio",
        operador="José",
    )
    assert uso.pk is not None
    maquina.refresh_from_db()
    assert maquina.horimetro_atual == horimetro_inicial + Decimal("4.50")

    services.delete_uso_maquina(uso)
    maquina.refresh_from_db()
    assert maquina.horimetro_atual == horimetro_inicial


# ── Services: Manutencao & Programacao ────────────────────────────────────────

@pytest.mark.django_db
def test_create_manutencao_e_programacao(user, maquina, safra):
    prog = services.create_programacao_manutencao(
        owner=user,
        maquina_id=maquina.id,
        descricao="Troca de óleo preventiva",
        criterio="data",
        data_limite="2026-02-15",
    )
    assert prog.pk is not None
    assert prog.concluida is False

    services.resolve_programacao_manutencao(prog)
    prog.refresh_from_db()
    assert prog.concluida is True


# ── Selectors ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_selectors_consolidado_e_alertas(user, maquina, talhao, safra):
    services.create_uso_maquina(
        owner=user,
        maquina_id=maquina.id,
        talhao_id=talhao.id,
        safra_id=safra.id,
        data="2026-01-20",
        hora_inicio="08:00:00",
        hora_fim="12:00:00",
        horas_trabalhadas=5.00,
        atividade="plantio",
    )
    
    services.create_abastecimento(
        owner=user,
        maquina_id=maquina.id,
        safra_id=safra.id,
        data="2026-01-20",
        tipo_combustivel="Diesel S10",
        quantidade=100.0,
        valor_total=600.0,
    )

    services.create_manutencao(
        owner=user,
        maquina_id=maquina.id,
        safra_id=safra.id,
        tipo="preventiva",
        data="2026-01-22",
        descricao="Revisão periódica",
        custo=1500.00,
    )

    res = selectors.get_consolidado_custos(owner=user, propriedade_id=maquina.propriedade_id)
    assert res["custo_combustivel"] == 600.0
    assert res["custo_manutencao"] == 1500.0
    assert res["custo_horas_maquina"] == 750.0
    assert res["custo_total"] == 2850.0

    hist = selectors.get_historico_maquina(owner=user, maquina_id=maquina.id)
    assert hist["indicadores"]["total_combustivel"] == 600.0
    assert hist["indicadores"]["total_manutencao"] == 1500.0
    assert hist["indicadores"]["total_horas"] == 5.0

    prog = services.create_programacao_manutencao(
        owner=user,
        maquina_id=maquina.id,
        descricao="Troca filtro de ar",
        criterio="horimetro",
        horimetro_limite=170.0,
        horas_alerta=20.0,
    )
    alertas = selectors.get_alertas_manutencao(user, maquina.propriedade_id)
    assert len(alertas) == 1
    assert alertas[0]["maquina_nome"] == maquina.nome


# ── API REST ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_api_maquina_crud(client_auth, propriedade):
    resp = client_auth.get(f"/api/v1/propriedades/{propriedade.id}/operacional/maquinas/")
    assert resp.status_code == 200
    assert len(resp.data) == 0

    payload = {
        "nome": "Trator Valmet",
        "modelo": "85",
        "categoria": "trator",
        "horimetro_atual": 1000.0,
        "custo_hora": 90.0,
    }
    resp = client_auth.post(
        f"/api/v1/propriedades/{propriedade.id}/operacional/maquinas/", payload, format="json"
    )
    assert resp.status_code == 201
    maquina_id = resp.data["id"]

    resp = client_auth.get(
        f"/api/v1/propriedades/{propriedade.id}/operacional/maquinas/{maquina_id}/"
    )
    assert resp.status_code == 200
    assert resp.data["nome"] == "Trator Valmet"

    resp = client_auth.patch(
        f"/api/v1/propriedades/{propriedade.id}/operacional/maquinas/{maquina_id}/",
        {"nome": "Trator Valmet II"},
        format="json"
    )
    assert resp.status_code == 200
    assert resp.data["nome"] == "Trator Valmet II"

    resp = client_auth.delete(
        f"/api/v1/propriedades/{propriedade.id}/operacional/maquinas/{maquina_id}/"
    )
    assert resp.status_code == 204
