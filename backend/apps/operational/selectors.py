# apps/operational/selectors.py
# Python 3.12+ | Django 5.x

from datetime import date
from django.db import models
from django.db.models import Sum, F
from django.utils import timezone
from .models import Maquina, Abastecimento, UsoMaquina, Manutencao, ProgramacaoManutencao


def get_maquinas_by_propriedade(owner, propriedade_id) -> models.QuerySet:
    """Retorna todas as máquinas ativas de uma propriedade do usuário."""
    return Maquina.objects.filter(
        owner=owner,
        propriedade_id=propriedade_id,
        is_active=True
    )


def get_maquina_by_id(owner, maquina_id) -> Maquina:
    """Retorna uma máquina ativa específica do usuário."""
    return Maquina.objects.get(owner=owner, id=maquina_id, is_active=True)


def get_abastecimentos_by_propriedade(
    owner,
    propriedade_id,
    maquina_id=None,
    safra_id=None,
    data_inicio=None,
    data_fim=None,
) -> models.QuerySet:
    """Retorna abastecimentos filtrados para as máquinas da propriedade."""
    queryset = Abastecimento.objects.filter(
        owner=owner,
        maquina__propriedade_id=propriedade_id,
        maquina__is_active=True
    )
    if maquina_id:
        queryset = queryset.filter(maquina_id=maquina_id)
    if safra_id:
        queryset = queryset.filter(safra_id=safra_id)
    if data_inicio:
        queryset = queryset.filter(data__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data__lte=data_fim)
    return queryset


def get_usos_by_propriedade(
    owner,
    propriedade_id,
    maquina_id=None,
    safra_id=None,
    talhao_id=None,
    data_inicio=None,
    data_fim=None,
) -> models.QuerySet:
    """Retorna os registros de uso de máquinas filtrados para a propriedade."""
    queryset = UsoMaquina.objects.filter(
        owner=owner,
        maquina__propriedade_id=propriedade_id,
        maquina__is_active=True
    )
    if maquina_id:
        queryset = queryset.filter(maquina_id=maquina_id)
    if safra_id:
        queryset = queryset.filter(safra_id=safra_id)
    if talhao_id:
        queryset = queryset.filter(talhao_id=talhao_id)
    if data_inicio:
        queryset = queryset.filter(data__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data__lte=data_fim)
    return queryset


def get_manutencoes_by_propriedade(
    owner,
    propriedade_id,
    maquina_id=None,
    safra_id=None,
    tipo=None,
    data_inicio=None,
    data_fim=None,
) -> models.QuerySet:
    """Retorna manutenções executadas filtradas para a propriedade."""
    queryset = Manutencao.objects.filter(
        owner=owner,
        maquina__propriedade_id=propriedade_id,
        maquina__is_active=True
    )
    if maquina_id:
        queryset = queryset.filter(maquina_id=maquina_id)
    if safra_id:
        queryset = queryset.filter(safra_id=safra_id)
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    if data_inicio:
        queryset = queryset.filter(data__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data__lte=data_fim)
    return queryset


def get_programacoes_by_propriedade(
    owner,
    propriedade_id,
    maquina_id=None,
    concluida=False,
) -> models.QuerySet:
    """Retorna programações de manutenção futura para a propriedade."""
    queryset = ProgramacaoManutencao.objects.filter(
        owner=owner,
        maquina__propriedade_id=propriedade_id,
        maquina__is_active=True,
        concluida=concluida
    )
    if maquina_id:
        queryset = queryset.filter(maquina_id=maquina_id)
    return queryset


def get_alertas_manutencao(owner, propriedade_id) -> list:
    """
    Retorna as programações de manutenção pendentes que atingiram os limites de alerta (RF-25).
    Cada item na lista incluirá metadados sobre o alerta (status: 'critico' ou 'alerta').
    """
    programacoes = get_programacoes_by_propriedade(owner, propriedade_id, concluida=False)
    alertas = []
    today = date.today()

    for p in programacoes:
        maquina = p.maquina
        status_alerta = None
        motivo = ""

        status_data = None
        motivo_data = ""
        if p.criterio in ("data", "ambos") and p.data_limite:
            delta_dias = (p.data_limite - today).days
            if delta_dias < 0:
                status_data = "critico"
                motivo_data = f"Atrasada há {-delta_dias} dias (limite: {p.data_limite.strftime('%d/%m/%Y')})"
            elif delta_dias <= p.dias_alerta:
                status_data = "alerta"
                motivo_data = f"Próxima do vencimento: restam {delta_dias} dias (limite: {p.data_limite.strftime('%d/%m/%Y')})"

        status_horimetro = None
        motivo_horimetro = ""
        if p.criterio in ("horimetro", "ambos") and p.horimetro_limite is not None:
            horas_restantes = p.horimetro_limite - maquina.horimetro_atual
            if horas_restantes < 0:
                status_horimetro = "critico"
                motivo_horimetro = f"Horímetro excedido em {-horas_restantes} horas (limite: {p.horimetro_limite}h, atual: {maquina.horimetro_atual}h)"
            elif horas_restantes <= p.horas_alerta:
                status_horimetro = "alerta"
                motivo_horimetro = f"Próxima do limite de horas: restam {horas_restantes} horas (limite: {p.horimetro_limite}h, atual: {maquina.horimetro_atual}h)"

        if status_data == "critico" or status_horimetro == "critico":
            status_alerta = "critico"
            motivo = " | ".join(filter(None, [motivo_data, motivo_horimetro]))
        elif status_data == "alerta" or status_horimetro == "alerta":
            status_alerta = "alerta"
            motivo = " | ".join(filter(None, [motivo_data, motivo_horimetro]))

        if status_alerta:
            alertas.append({
                "id": p.id,
                "maquina_id": maquina.id,
                "maquina_nome": maquina.nome,
                "descricao": p.descricao,
                "criterio": p.criterio,
                "status": status_alerta,
                "motivo": motivo,
                "data_limite": p.data_limite,
                "horimetro_limite": p.horimetro_limite,
            })
            
    return alertas


def get_consolidado_custos(
    owner,
    propriedade_id,
    safra_id=None,
    talhao_id=None,
    cultura=None,
    data_inicio=None,
    data_fim=None,
) -> dict:
    """
    Calcula e consolida automaticamente os custos operacionais (RF-27).
    Retorna totais consolidados para Combustível, Manutenção e Horas-Máquina.
    """
    # 1. Obter QuerySets iniciais filtrados por propriedade e proprietário
    abastecimentos = Abastecimento.objects.filter(
        owner=owner,
        maquina__propriedade_id=propriedade_id,
        maquina__is_active=True
    )
    manutencoes = Manutencao.objects.filter(
        owner=owner,
        maquina__propriedade_id=propriedade_id,
        maquina__is_active=True
    )
    usos = UsoMaquina.objects.filter(
        owner=owner,
        maquina__propriedade_id=propriedade_id,
        maquina__is_active=True
    )

    # 2. Aplicar Filtro de Safra
    if safra_id:
        abastecimentos = abastecimentos.filter(safra_id=safra_id)
        manutencoes = manutencoes.filter(safra_id=safra_id)
        usos = usos.filter(safra_id=safra_id)

    # 3. Aplicar Filtro de Cultura (a partir de safra__cultura)
    if cultura:
        abastecimentos = abastecimentos.filter(safra__cultura=cultura)
        manutencoes = manutencoes.filter(safra__cultura=cultura)
        usos = usos.filter(safra__cultura=cultura)

    # 4. Aplicar Filtro de Período
    if data_inicio:
        abastecimentos = abastecimentos.filter(data__gte=data_inicio)
        manutencoes = manutencoes.filter(data__gte=data_inicio)
        usos = usos.filter(data__gte=data_inicio)
    if data_fim:
        abastecimentos = abastecimentos.filter(data__lte=data_fim)
        manutencoes = manutencoes.filter(data__lte=data_fim)
        usos = usos.filter(data__lte=data_fim)

    # 5. Aplicar Filtro de Talhão
    if talhao_id:
        # Usos são filtrados diretamente pelo talhao_id
        usos = usos.filter(talhao_id=talhao_id)
        
        # Para combustível e manutenção, atribuímos se a máquina trabalhou no talhão no período/safra
        maquinas_do_talhao = usos.values_list("maquina_id", flat=True)
        abastecimentos = abastecimentos.filter(maquina_id__in=maquinas_do_talhao)
        manutencoes = manutencoes.filter(maquina_id__in=maquinas_do_talhao)

    # 6. Agregações
    from decimal import Decimal
    total_combustivel = Decimal(abastecimentos.aggregate(total=Sum("valor_total"))["total"] or 0)
    total_manutencao = Decimal(manutencoes.aggregate(total=Sum("custo"))["total"] or 0)

    # Para horas-máquina: somatório de (horas_trabalhadas * maquina__custo_hora)
    total_horas_maquina = Decimal(usos.annotate(
        custo_op=F("horas_trabalhadas") * F("maquina__custo_hora")
    ).aggregate(total=Sum("custo_op"))["total"] or 0)

    # Total de horas registradas
    total_horas = Decimal(usos.aggregate(total=Sum("horas_trabalhadas"))["total"] or 0)

    return {
        "custo_combustivel": float(total_combustivel),
        "custo_manutencao": float(total_manutencao),
        "custo_horas_maquina": float(total_horas_maquina),
        "custo_total": float(total_combustivel + total_manutencao + total_horas_maquina),
        "total_horas_trabalhadas": float(total_horas),
        "abastecimentos_quantidade": abastecimentos.count(),
    }


def get_historico_maquina(owner, maquina_id) -> dict:
    """
    Retorna o perfil completo e histórico de ciclo de vida de um equipamento (RF-28).
    """
    maquina = get_maquina_by_id(owner, maquina_id)

    abastecimentos = Abastecimento.objects.filter(maquina=maquina)
    usos = UsoMaquina.objects.filter(maquina=maquina)
    manutencoes = Manutencao.objects.filter(maquina=maquina)

    # Indicadores
    total_gasto_combustivel = abastecimentos.aggregate(total=Sum("valor_total"))["total"] or 0.0
    total_gasto_manutencao = manutencoes.aggregate(total=Sum("custo"))["total"] or 0.0
    total_horas_trabalhadas = usos.aggregate(total=Sum("horas_trabalhadas"))["total"] or 0.0

    custo_operacional_uso = usos.annotate(
        custo_op=F("horas_trabalhadas") * F("maquina__custo_hora")
    ).aggregate(total=Sum("custo_op"))["total"] or 0.0

    custo_operacional_acumulado = total_gasto_combustivel + total_gasto_manutencao + custo_operacional_uso

    # Talhões atendidos (únicos)
    talhoes_ids = usos.values_list("talhao_id", "talhao__nome").distinct()
    talhoes_atendidos = [{"id": t[0], "nome": t[1]} for t in talhoes_ids if t[0] is not None]

    # Safras vinculadas (únicas de qualquer dos registros)
    safras_abast = abastecimentos.values_list("safra_id", "safra__nome")
    safras_usos = usos.values_list("safra_id", "safra__nome")
    safras_manut = manutencoes.values_list("safra_id", "safra__nome")
    
    safras_set = set(safras_abast) | set(safras_usos) | set(safras_manut)
    safras_vinculadas = [{"id": s[0], "nome": s[1]} for s in safras_set if s[0] is not None]

    # Listas detalhadas para o histórico
    abastecimentos_list = [{
        "id": ab.id,
        "data": ab.data.isoformat() if hasattr(ab.data, "isoformat") else str(ab.data),
        "tipo_combustivel": ab.tipo_combustivel,
        "quantidade": float(ab.quantidade),
        "valor_total": float(ab.valor_total),
        "horimetro": float(ab.horimetro) if ab.horimetro is not None else None,
        "observacao": ab.observacao,
        "safra_nome": ab.safra.nome,
    } for ab in abastecimentos]

    manutencoes_list = [{
        "id": mn.id,
        "data": mn.data.isoformat() if hasattr(mn.data, "isoformat") else str(mn.data),
        "tipo": mn.tipo,
        "tipo_display": mn.get_tipo_display(),
        "descricao": mn.descricao,
        "custo": float(mn.custo),
        "fornecedor": mn.fornecedor,
        "observacao": mn.observacao,
        "safra_nome": mn.safra.nome,
    } for mn in manutencoes]

    usos_list = [{
        "id": us.id,
        "data": us.data.isoformat() if hasattr(us.data, "isoformat") else str(us.data),
        "horas_trabalhadas": float(us.horas_trabalhadas),
        "atividade": us.atividade,
        "atividade_display": us.get_atividade_display(),
        "operador": us.operador,
        "observacao": us.observacao,
        "talhao_nome": us.talhao.nome,
        "safra_nome": us.safra.nome,
    } for us in usos]

    return {
        "maquina": {
            "id": maquina.id,
            "nome": maquina.nome,
            "modelo": maquina.modelo,
            "categoria": maquina.categoria,
            "categoria_display": maquina.get_categoria_display(),
            "horimetro_atual": float(maquina.horimetro_atual),
            "custo_hora": float(maquina.custo_hora),
        },
        "indicadores": {
            "total_gasto_combustivel": float(total_gasto_combustivel),
            "total_gasto_manutencao": float(total_gasto_manutencao),
            "total_horas_trabalhadas": float(total_horas_trabalhadas),
            "custo_operacional_acumulado": float(custo_operacional_acumulado),
            # Chaves para compatibilidade com o teste unitário
            "total_combustivel": float(total_gasto_combustivel),
            "total_manutencao": float(total_gasto_manutencao),
            "total_horas": float(total_horas_trabalhadas),
        },
        "talhoes_atendidos": talhoes_atendidos,
        "safras_vinculadas": safras_vinculadas,
        "abastecimentos": abastecimentos_list,
        "manutencoes": manutencoes_list,
        "usos": usos_list,
    }
