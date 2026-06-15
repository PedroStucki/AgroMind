# apps/operational/models.py
# Python 3.12+ | Django 5.x

from django.conf import settings
from django.db import models


class CategoriaMaquina(models.TextChoices):
    TRATOR = "trator", "Trator"
    COLHEITADEIRA = "colheitadeira", "Colheitadeira"
    PULVERIZADOR = "pulverizador", "Pulverizador"
    SEMEADORA = "semeadora", "Semeadora"
    PLANTADEIRA = "plantadeira", "Plantadeira"
    CAMINHAO = "caminhao", "Caminhão"
    IMPLEMENTO = "implemento", "Implemento"
    OUTRO = "outro", "Outro"


class AtividadeMaquina(models.TextChoices):
    PLANTIO = "plantio", "Plantio"
    PULVERIZACAO = "pulverizacao", "Pulverização"
    ADUBACAO = "adubacao", "Adubação"
    COLHEITA = "colheita", "Colheita"
    TRANSPORTE = "transporte", "Transporte"
    PREPARO_SOLO = "preparo_solo", "Preparo de Solo"
    OUTRO = "outro", "Outro"


class TipoManutencao(models.TextChoices):
    PREVENTIVA = "preventiva", "Preventiva"
    CORRETIVA = "corretiva", "Corretiva"


class CriterioProgramacao(models.TextChoices):
    DATA = "data", "Data"
    HORIMETRO = "horimetro", "Horímetro"
    AMBOS = "ambos", "Ambos"



class Maquina(models.Model):
    """
    Representa uma máquina ou equipamento operacional da fazenda (propriedade).
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="maquinas",
        verbose_name="Proprietário",
    )
    propriedade = models.ForeignKey(
        "properties.Propriedade",
        on_delete=models.CASCADE,
        related_name="maquinas",
        verbose_name="Propriedade",
    )
    nome = models.CharField(max_length=120, verbose_name="Nome da máquina")
    modelo = models.CharField(max_length=120, blank=True, default="", verbose_name="Modelo")
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaMaquina.choices,
        default=CategoriaMaquina.OUTRO,
        verbose_name="Categoria",
    )
    horimetro_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Horímetro atual",
    )
    custo_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Custo por hora (R$)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Máquina / Equipamento"
        verbose_name_plural = "Máquinas / Equipamentos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"


class Abastecimento(models.Model):
    """
    Registro de abastecimento de uma máquina associada a uma safra (RF-22).
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="abastecimentos",
        verbose_name="Proprietário",
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name="abastecimentos",
        verbose_name="Máquina",
    )
    safra = models.ForeignKey(
        "planting.Safra",
        on_delete=models.CASCADE,
        related_name="abastecimentos",
        verbose_name="Safra",
    )
    data = models.DateField(verbose_name="Data")
    tipo_combustivel = models.CharField(max_length=50, verbose_name="Tipo de combustível")
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade (litros)",
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor total (R$)",
    )
    horimetro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horímetro",
    )
    observacao = models.TextField(blank=True, default="", verbose_name="Observação")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Abastecimento"
        verbose_name_plural = "Abastecimentos"
        ordering = ["-data", "-created_at"]

    def __str__(self):
        return f"Abastecimento {self.maquina.nome} — {self.quantidade}L em {self.data}"


class UsoMaquina(models.Model):
    """
    Registro de utilização operacional de uma máquina em um talhão e safra (RF-23).
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="usos_maquina",
        verbose_name="Proprietário",
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name="usos",
        verbose_name="Máquina",
    )
    talhao = models.ForeignKey(
        "properties.Talhao",
        on_delete=models.CASCADE,
        related_name="usos_maquina",
        verbose_name="Talhão",
    )
    safra = models.ForeignKey(
        "planting.Safra",
        on_delete=models.CASCADE,
        related_name="usos_maquina",
        verbose_name="Safra",
    )
    data = models.DateField(verbose_name="Data")
    hora_inicio = models.TimeField(verbose_name="Hora Início")
    hora_fim = models.TimeField(verbose_name="Hora Fim")
    horas_trabalhadas = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Horas trabalhadas",
    )
    atividade = models.CharField(
        max_length=30,
        choices=AtividadeMaquina.choices,
        default=AtividadeMaquina.OUTRO,
        verbose_name="Atividade",
    )
    operador = models.CharField(max_length=120, blank=True, default="", verbose_name="Operador")
    observacao = models.TextField(blank=True, default="", verbose_name="Observação")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Uso de Máquina"
        verbose_name_plural = "Uso de Máquinas"
        ordering = ["-data", "-created_at"]

    def __str__(self):
        return f"Uso {self.maquina.nome} — {self.horas_trabalhadas}h em {self.data}"


class Manutencao(models.Model):
    """
    Registro de manutenções preventivas e corretivas executadas em equipamentos (RF-24).
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="manutencoes",
        verbose_name="Proprietário",
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name="manutencoes",
        verbose_name="Máquina / Equipamento",
    )
    safra = models.ForeignKey(
        "planting.Safra",
        on_delete=models.CASCADE,
        related_name="manutencoes",
        verbose_name="Safra",
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoManutencao.choices,
        default=TipoManutencao.PREVENTIVA,
        verbose_name="Tipo de manutenção",
    )
    data = models.DateField(verbose_name="Data")
    descricao = models.TextField(verbose_name="Descrição")
    custo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Custo (R$)",
    )
    fornecedor = models.CharField(max_length=200, blank=True, default="", verbose_name="Fornecedor")
    observacao = models.TextField(blank=True, default="", verbose_name="Observação")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manutenção"
        verbose_name_plural = "Manutenções"
        ordering = ["-data", "-created_at"]

    def __str__(self):
        return f"Manutenção {self.get_tipo_display()} {self.maquina.nome} — R$ {self.custo} em {self.data}"


class ProgramacaoManutencao(models.Model):
    """
    Programação de manutenções futuras preventivas (RF-25).
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="programacoes_manutencao",
        verbose_name="Proprietário",
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name="programacoes",
        verbose_name="Máquina",
    )
    descricao = models.TextField(verbose_name="Descrição do serviço")
    criterio = models.CharField(
        max_length=20,
        choices=CriterioProgramacao.choices,
        default=CriterioProgramacao.DATA,
        verbose_name="Critério",
    )
    data_limite = models.DateField(null=True, blank=True, verbose_name="Data limite")
    horimetro_limite = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horímetro limite",
    )
    dias_alerta = models.IntegerField(
        default=15,
        verbose_name="Dias de antecedência para alerta",
    )
    horas_alerta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=20.0,
        verbose_name="Horas restantes de horímetro para alerta",
    )
    concluida = models.BooleanField(default=False, verbose_name="Concluída")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programação de Manutenção"
        verbose_name_plural = "Programações de Manutenção"
        ordering = ["concluida", "data_limite", "horimetro_limite"]

    def __str__(self):
        return f"Programação {self.maquina.nome} — {self.descricao[:30]}"
