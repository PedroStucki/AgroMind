# apps/operational/serializers.py
# Python 3.12+ | Django 5.x

from rest_framework import serializers
from .models import Maquina, Abastecimento, UsoMaquina, Manutencao, ProgramacaoManutencao


# ── Maquina ───────────────────────────────────────────────────────────────────

class MaquinaSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source="get_categoria_display", read_only=True)

    class Meta:
        model = Maquina
        fields = [
            "id", "nome", "modelo", "categoria", "categoria_display",
            "horimetro_atual", "custo_hora", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MaquinaCreateSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=120)
    modelo = serializers.CharField(max_length=120, required=False, default="")
    categoria = serializers.ChoiceField(choices=Maquina.categoria.field.choices, required=False, default="outro")
    horimetro_atual = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    custo_hora = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)


class MaquinaUpdateSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=120, required=False)
    modelo = serializers.CharField(max_length=120, required=False)
    categoria = serializers.ChoiceField(choices=Maquina.categoria.field.choices, required=False)
    horimetro_atual = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    custo_hora = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


# ── Abastecimento ──────────────────────────────────────────────────────────────

class AbastecimentoSerializer(serializers.ModelSerializer):
    maquina_nome = serializers.CharField(source="maquina.nome", read_only=True)
    safra_nome = serializers.CharField(source="safra.nome", read_only=True)

    class Meta:
        model = Abastecimento
        fields = [
            "id", "maquina", "maquina_nome", "safra", "safra_nome",
            "data", "tipo_combustivel", "quantidade", "valor_total",
            "horimetro", "observacao", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AbastecimentoCreateSerializer(serializers.Serializer):
    maquina_id = serializers.IntegerField()
    safra_id = serializers.IntegerField()
    data = serializers.DateField()
    tipo_combustivel = serializers.CharField(max_length=50)
    quantidade = serializers.DecimalField(max_digits=10, decimal_places=2)
    valor_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    horimetro = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    observacao = serializers.CharField(required=False, default="", allow_blank=True)


class AbastecimentoUpdateSerializer(serializers.Serializer):
    safra_id = serializers.IntegerField(required=False)
    data = serializers.DateField(required=False)
    tipo_combustivel = serializers.CharField(max_length=50, required=False)
    quantidade = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    valor_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    horimetro = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    observacao = serializers.CharField(required=False, allow_blank=True)


# ── UsoMaquina ────────────────────────────────────────────────────────────────

class UsoMaquinaSerializer(serializers.ModelSerializer):
    maquina_nome = serializers.CharField(source="maquina.nome", read_only=True)
    talhao_nome = serializers.CharField(source="talhao.nome", read_only=True)
    safra_nome = serializers.CharField(source="safra.nome", read_only=True)
    atividade_display = serializers.CharField(source="get_atividade_display", read_only=True)
    custo_operacional = serializers.SerializerMethodField()

    class Meta:
        model = UsoMaquina
        fields = [
            "id", "maquina", "maquina_nome", "talhao", "talhao_nome",
            "safra", "safra_nome", "data", "hora_inicio", "hora_fim",
            "horas_trabalhadas", "atividade", "atividade_display",
            "operador", "observacao", "custo_operacional", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_custo_operacional(self, obj):
        return float(obj.horas_trabalhadas * obj.maquina.custo_hora)


class UsoMaquinaCreateSerializer(serializers.Serializer):
    maquina_id = serializers.IntegerField()
    talhao_id = serializers.IntegerField()
    safra_id = serializers.IntegerField()
    data = serializers.DateField()
    hora_inicio = serializers.TimeField()
    hora_fim = serializers.TimeField()
    horas_trabalhadas = serializers.DecimalField(max_digits=6, decimal_places=2)
    atividade = serializers.ChoiceField(choices=UsoMaquina.atividade.field.choices, default="outro")
    operador = serializers.CharField(max_length=120, required=False, default="", allow_blank=True)
    observacao = serializers.CharField(required=False, default="", allow_blank=True)


class UsoMaquinaUpdateSerializer(serializers.Serializer):
    talhao_id = serializers.IntegerField(required=False)
    safra_id = serializers.IntegerField(required=False)
    data = serializers.DateField(required=False)
    hora_inicio = serializers.TimeField(required=False)
    hora_fim = serializers.TimeField(required=False)
    horas_trabalhadas = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    atividade = serializers.ChoiceField(choices=UsoMaquina.atividade.field.choices, required=False)
    operador = serializers.CharField(max_length=120, required=False, allow_blank=True)
    observacao = serializers.CharField(required=False, allow_blank=True)


# ── Manutencao ────────────────────────────────────────────────────────────────

class ManutencaoSerializer(serializers.ModelSerializer):
    maquina_nome = serializers.CharField(source="maquina.nome", read_only=True)
    safra_nome = serializers.CharField(source="safra.nome", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Manutencao
        fields = [
            "id", "maquina", "maquina_nome", "safra", "safra_nome",
            "tipo", "tipo_display", "data", "descricao", "custo",
            "fornecedor", "observacao", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ManutencaoCreateSerializer(serializers.Serializer):
    maquina_id = serializers.IntegerField()
    safra_id = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=Manutencao.tipo.field.choices)
    data = serializers.DateField()
    descricao = serializers.CharField()
    custo = serializers.DecimalField(max_digits=12, decimal_places=2)
    fornecedor = serializers.CharField(max_length=200, required=False, default="", allow_blank=True)
    observacao = serializers.CharField(required=False, default="", allow_blank=True)


class ManutencaoUpdateSerializer(serializers.Serializer):
    safra_id = serializers.IntegerField(required=False)
    tipo = serializers.ChoiceField(choices=Manutencao.tipo.field.choices, required=False)
    data = serializers.DateField(required=False)
    descricao = serializers.CharField(required=False)
    custo = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    fornecedor = serializers.CharField(max_length=200, required=False, allow_blank=True)
    observacao = serializers.CharField(required=False, allow_blank=True)


# ── ProgramacaoManutencao ─────────────────────────────────────────────────────

class ProgramacaoManutencaoSerializer(serializers.ModelSerializer):
    maquina_nome = serializers.CharField(source="maquina.nome", read_only=True)
    criterio_display = serializers.CharField(source="get_criterio_display", read_only=True)
    horimetro_atual_maquina = serializers.DecimalField(
        source="maquina.horimetro_atual", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = ProgramacaoManutencao
        fields = [
            "id", "maquina", "maquina_nome", "horimetro_atual_maquina",
            "descricao", "criterio", "criterio_display",
            "data_limite", "horimetro_limite", "dias_alerta", "horas_alerta",
            "concluida", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProgramacaoCreateSerializer(serializers.Serializer):
    maquina_id = serializers.IntegerField()
    descricao = serializers.CharField()
    criterio = serializers.ChoiceField(choices=ProgramacaoManutencao.criterio.field.choices)
    data_limite = serializers.DateField(required=False, allow_null=True)
    horimetro_limite = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    dias_alerta = serializers.IntegerField(required=False, default=15)
    horas_alerta = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=20.0)


class ProgramacaoUpdateSerializer(serializers.Serializer):
    descricao = serializers.CharField(required=False)
    criterio = serializers.ChoiceField(choices=ProgramacaoManutencao.criterio.field.choices, required=False)
    data_limite = serializers.DateField(required=False, allow_null=True)
    horimetro_limite = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    dias_alerta = serializers.IntegerField(required=False)
    horas_alerta = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    concluida = serializers.BooleanField(required=False)
