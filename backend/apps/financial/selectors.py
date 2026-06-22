# apps/financial/selectors.py
from datetime import date
from django.db.models import Sum
from decimal import Decimal

from apps.planting.models import Safra
from apps.properties.models import Talhao
from apps.operational.selectors import get_consolidado_custos
from apps.operational.models import Abastecimento, Manutencao, UsoMaquina

from .models import Despesa, Receita

def get_receita_total(owner, propriedade_id, safra_id=None) -> Decimal:
    qs = Receita.objects.filter(owner=owner, propriedade_id=propriedade_id)
    if safra_id:
        qs = qs.filter(safra_id=safra_id)
    total = qs.aggregate(total=Sum("valor_total"))["total"]
    return Decimal(total or 0)

def get_despesa_financeira_total(owner, propriedade_id, safra_id=None) -> Decimal:
    qs = Despesa.objects.filter(owner=owner, propriedade_id=propriedade_id)
    if safra_id:
        qs = qs.filter(safra_id=safra_id)
    total = qs.aggregate(total=Sum("valor"))["total"]
    return Decimal(total or 0)

def get_producao_total(owner, propriedade_id, safra_id=None) -> Decimal:
    # Usando a soma das quantidades vendidas nas receitas como "Produção Total"
    qs = Receita.objects.filter(owner=owner, propriedade_id=propriedade_id)
    if safra_id:
        qs = qs.filter(safra_id=safra_id)
    total = qs.aggregate(total=Sum("quantidade"))["total"]
    return Decimal(total or 0)

def get_area_total(owner, propriedade_id, safra_id=None) -> Decimal:
    # Para calcular custo por hectare, precisamos somar a área dos talhões da safra
    if safra_id:
        safra = Safra.objects.filter(owner=owner, id=safra_id).first()
        if safra:
            total_area = safra.talhoes.aggregate(total=Sum("area"))["total"]
            return Decimal(total_area or 0)
    
    # Se não há safra específica, não temos como determinar a área plantada com precisão aqui
    return Decimal(0)

def get_consolidado_financeiro(owner, propriedade_id, safra_id=None) -> dict:
    # Receitas Diretas (Financeiro)
    receita_total = get_receita_total(owner, propriedade_id, safra_id)

    # Despesas Diretas (Financeiro)
    despesa_financeira = get_despesa_financeira_total(owner, propriedade_id, safra_id)

    # Custos Operacionais (do Módulo Operacional)
    consolidado_op = get_consolidado_custos(owner, propriedade_id, safra_id=safra_id)
    custo_operacional = Decimal(consolidado_op.get("custo_total", 0))

    custo_total = despesa_financeira + custo_operacional

    # Insumos (assumindo a categoria Insumos de Despesas e parte operacional se houver, 
    # mas focando em despesas de categoria 'insumos')
    qs_insumos = Despesa.objects.filter(owner=owner, propriedade_id=propriedade_id, categoria="insumos")
    if safra_id:
        qs_insumos = qs_insumos.filter(safra_id=safra_id)
    custo_insumos = Decimal(qs_insumos.aggregate(total=Sum("valor"))["total"] or 0)

    # Indicadores Calculados
    lucro_liquido = receita_total - custo_total

    roi = Decimal(0)
    if custo_total > 0:
        roi = (lucro_liquido / custo_total) * 100

    margem_bruta = Decimal(0)
    if receita_total > 0:
        margem_bruta = ((receita_total - custo_insumos) / receita_total) * 100

    margem_liquida = Decimal(0)
    if receita_total > 0:
        margem_liquida = (lucro_liquido / receita_total) * 100

    area_total = get_area_total(owner, propriedade_id, safra_id)
    custo_por_hectare = Decimal(0)
    if area_total > 0:
        custo_por_hectare = custo_total / area_total

    producao_total = get_producao_total(owner, propriedade_id, safra_id)
    custo_por_saca = Decimal(0)
    preco_medio_venda = Decimal(0)
    if producao_total > 0:
        custo_por_saca = custo_total / producao_total
        preco_medio_venda = receita_total / producao_total

    ponto_equilibrio = Decimal(0)
    if preco_medio_venda > 0:
        ponto_equilibrio = custo_total / preco_medio_venda

    return {
        "receita_total": float(receita_total),
        "despesa_financeira": float(despesa_financeira),
        "custo_operacional": float(custo_operacional),
        "custo_total": float(custo_total),
        "lucro_liquido": float(lucro_liquido),
        "roi": float(roi),
        "margem_bruta": float(margem_bruta),
        "margem_liquida": float(margem_liquida),
        "custo_por_hectare": float(custo_por_hectare),
        "custo_por_saca": float(custo_por_saca),
        "ponto_equilibrio": float(ponto_equilibrio),
        "area_total_ha": float(area_total),
        "producao_total": float(producao_total),
    }

def get_fluxo_caixa_cronologico(owner, propriedade_id, safra_id=None) -> list:
    """
    Retorna uma lista ordenada cronologicamente contendo:
    - Receitas (Entradas)
    - Despesas (Saídas Diretas)
    - Abastecimentos (Saídas Operacionais)
    - Manutenções (Saídas Operacionais)
    - UsoMaquina (Custo hora-máquina, opcional no fluxo real, mas compõe o custo)
    Calcula o saldo acumulado.
    """
    eventos = []

    # 1. Receitas
    qs_rec = Receita.objects.filter(owner=owner, propriedade_id=propriedade_id)
    if safra_id:
        qs_rec = qs_rec.filter(safra_id=safra_id)
    for rec in qs_rec:
        eventos.append({
            "tipo": "receita",
            "categoria": "Venda",
            "descricao": f"Venda de {rec.produto} para {rec.comprador}",
            "data": rec.data_venda,
            "valor": rec.valor_total,
            "sinal": 1
        })

    # 2. Despesas
    qs_desp = Despesa.objects.filter(owner=owner, propriedade_id=propriedade_id)
    if safra_id:
        qs_desp = qs_desp.filter(safra_id=safra_id)
    for desp in qs_desp:
        eventos.append({
            "tipo": "despesa",
            "categoria": desp.get_categoria_display(),
            "descricao": desp.descricao,
            "data": desp.data,
            "valor": desp.valor,
            "sinal": -1
        })

    # 3. Abastecimentos
    qs_abast = Abastecimento.objects.filter(owner=owner, maquina__propriedade_id=propriedade_id)
    if safra_id:
        qs_abast = qs_abast.filter(safra_id=safra_id)
    for abast in qs_abast:
        eventos.append({
            "tipo": "operacional_abastecimento",
            "categoria": "Combustível",
            "descricao": f"Abastecimento {abast.maquina.nome} ({abast.tipo_combustivel})",
            "data": abast.data,
            "valor": abast.valor_total,
            "sinal": -1
        })

    # 4. Manutenções
    qs_manut = Manutencao.objects.filter(owner=owner, maquina__propriedade_id=propriedade_id)
    if safra_id:
        qs_manut = qs_manut.filter(safra_id=safra_id)
    for manut in qs_manut:
        eventos.append({
            "tipo": "operacional_manutencao",
            "categoria": "Manutenção",
            "descricao": f"Manutenção {manut.get_tipo_display()} - {manut.maquina.nome}",
            "data": manut.data,
            "valor": manut.custo,
            "sinal": -1
        })

    # Ordenar por data
    eventos = sorted(eventos, key=lambda x: x["data"])

    # Calcular Saldo Acumulado
    saldo_acumulado = Decimal(0)
    for ev in eventos:
        saldo_acumulado += Decimal(ev["valor"]) * ev["sinal"]
        ev["saldo_acumulado"] = float(saldo_acumulado)
        # Formatar a data para json
        ev["data"] = ev["data"].isoformat() if hasattr(ev["data"], "isoformat") else str(ev["data"])
        ev["valor"] = float(ev["valor"])

    # Reverter ordenação para que o mais recente apareça primeiro na tabela? 
    # Depende de como o frontend vai mostrar, geralmente cronológico é antigo -> recente.
    # Vamos manter cronológico antigo -> recente.
    return eventos
