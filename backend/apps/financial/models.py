# apps/financial/models.py
from django.conf import settings
from django.db import models

class CategoriaDespesa(models.TextChoices):
    INSUMOS = "insumos", "Insumos"
    COMBUSTIVEL = "combustivel", "Combustível"
    MANUTENCAO = "manutencao", "Manutenção"
    MAO_DE_OBRA = "mao_de_obra", "Mão de Obra"
    OUTRO = "outro", "Outro"

class UnidadeMedida(models.TextChoices):
    SACAS = "sacas", "Sacas"
    KG = "kg", "Kg"
    TONELADA = "tonelada", "Tonelada"
    OUTRO = "outro", "Outro"


class Despesa(models.Model):
    """
    Representa uma despesa financeira avulsa vinculada a uma Safra.
    (RF-27)
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="despesas",
        verbose_name="Proprietário",
    )
    propriedade = models.ForeignKey(
        "properties.Propriedade",
        on_delete=models.CASCADE,
        related_name="despesas",
        verbose_name="Propriedade",
    )
    safra = models.ForeignKey(
        "planting.Safra",
        on_delete=models.CASCADE,
        related_name="despesas",
        verbose_name="Safra",
    )
    categoria = models.CharField(
        max_length=50,
        choices=CategoriaDespesa.choices,
        default=CategoriaDespesa.OUTRO,
        verbose_name="Categoria",
    )
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor (R$)")
    data = models.DateField(verbose_name="Data da Despesa")
    observacao = models.TextField(blank=True, default="", verbose_name="Observação")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ["-data", "-created_at"]

    def __str__(self):
        return f"Despesa: {self.descricao} (R$ {self.valor})"


class Receita(models.Model):
    """
    Representa uma receita proveniente da venda de produção da Safra.
    (RF-28)
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receitas",
        verbose_name="Proprietário",
    )
    propriedade = models.ForeignKey(
        "properties.Propriedade",
        on_delete=models.CASCADE,
        related_name="receitas",
        verbose_name="Propriedade",
    )
    safra = models.ForeignKey(
        "planting.Safra",
        on_delete=models.CASCADE,
        related_name="receitas",
        verbose_name="Safra",
    )
    comprador = models.CharField(max_length=200, verbose_name="Comprador")
    produto = models.CharField(max_length=150, verbose_name="Produto")
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade")
    unidade = models.CharField(
        max_length=20,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.SACAS,
        verbose_name="Unidade",
    )
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário (R$)")
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Total (R$)")
    data_venda = models.DateField(verbose_name="Data da Venda")
    observacao = models.TextField(blank=True, default="", verbose_name="Observação")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"
        ordering = ["-data_venda", "-created_at"]

    def __str__(self):
        return f"Receita: {self.produto} para {self.comprador} (R$ {self.valor_total})"

    def save(self, *args, **kwargs):
        # RF-28: Valor total deve ser calculado automaticamente.
        self.valor_total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
