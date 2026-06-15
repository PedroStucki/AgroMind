# apps/operational/admin.py
from django.contrib import admin
from .models import Maquina, Abastecimento, UsoMaquina, Manutencao, ProgramacaoManutencao


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ("nome", "propriedade", "categoria", "horimetro_atual", "custo_hora", "is_active")
    list_filter = ("propriedade", "categoria", "is_active")
    search_fields = ("nome", "modelo")


@admin.register(Abastecimento)
class AbastecimentoAdmin(admin.ModelAdmin):
    list_display = ("maquina", "safra", "data", "tipo_combustivel", "quantidade", "valor_total")
    list_filter = ("safra", "tipo_combustivel")
    search_fields = ("maquina__nome", "observacao")


@admin.register(UsoMaquina)
class UsoMaquinaAdmin(admin.ModelAdmin):
    list_display = ("maquina", "talhao", "safra", "data", "horas_trabalhadas", "atividade", "operador")
    list_filter = ("safra", "atividade", "talhao")
    search_fields = ("maquina__nome", "operador", "observacao")


@admin.register(Manutencao)
class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ("maquina", "safra", "tipo", "data", "custo", "fornecedor")
    list_filter = ("safra", "tipo", "data")
    search_fields = ("maquina__nome", "descricao", "fornecedor")


@admin.register(ProgramacaoManutencao)
class ProgramacaoManutencaoAdmin(admin.ModelAdmin):
    list_display = ("maquina", "criterio", "data_limite", "horimetro_limite", "concluida")
    list_filter = ("criterio", "concluida")
    search_fields = ("maquina__nome", "descricao")
