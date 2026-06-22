# apps/financial/serializers.py
from rest_framework import serializers
from .models import Despesa, Receita

class DespesaSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    safra_nome = serializers.CharField(source='safra.nome', read_only=True)

    class Meta:
        model = Despesa
        fields = [
            "id",
            "propriedade",
            "safra",
            "safra_nome",
            "categoria",
            "categoria_display",
            "descricao",
            "valor",
            "data",
            "observacao",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

class ReceitaSerializer(serializers.ModelSerializer):
    unidade_display = serializers.CharField(source='get_unidade_display', read_only=True)
    safra_nome = serializers.CharField(source='safra.nome', read_only=True)

    class Meta:
        model = Receita
        fields = [
            "id",
            "propriedade",
            "safra",
            "safra_nome",
            "comprador",
            "produto",
            "quantidade",
            "unidade",
            "unidade_display",
            "preco_unitario",
            "valor_total",
            "data_venda",
            "observacao",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["valor_total", "created_at", "updated_at"]
