# apps/operational/services.py
# Python 3.12+ | Django 5.x

from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Maquina, Abastecimento, UsoMaquina, Manutencao, ProgramacaoManutencao
from apps.properties.models import Talhao
from apps.planting.models import Safra


def create_maquina(
    owner,
    propriedade_id,
    nome: str,
    modelo: str = "",
    categoria: str = "outro",
    horimetro_atual=0.0,
    custo_hora=0.0,
) -> Maquina:
    """Cria um novo equipamento operacional."""
    if not nome:
        raise ValidationError("O nome da máquina é obrigatório.")
        
    maquina = Maquina(
        owner=owner,
        propriedade_id=propriedade_id,
        nome=nome,
        modelo=modelo,
        categoria=categoria,
        horimetro_atual=Decimal(str(horimetro_atual)),
        custo_hora=Decimal(str(custo_hora))
    )
    maquina.full_clean()
    maquina.save()
    return maquina


def update_maquina(
    maquina: Maquina,
    nome: str = None,
    modelo: str = None,
    categoria: str = None,
    horimetro_atual=None,
    custo_hora=None,
) -> Maquina:
    """Atualiza dados cadastrais de um equipamento."""
    if nome is not None:
        if not nome.strip():
            raise ValidationError("O nome da máquina não pode ficar em branco.")
        maquina.nome = nome
    if modelo is not None:
        maquina.modelo = modelo
    if categoria is not None:
        maquina.categoria = categoria
    if horimetro_atual is not None:
        maquina.horimetro_atual = Decimal(str(horimetro_atual))
    if custo_hora is not None:
        maquina.custo_hora = Decimal(str(custo_hora))

    maquina.full_clean()
    maquina.save()
    return maquina


def deactivate_maquina(maquina: Maquina) -> None:
    """Inativa logicamente a máquina (soft delete)."""
    maquina.is_active = False
    maquina.save()


def create_abastecimento(
    owner,
    maquina_id: int,
    safra_id: int,
    data,
    tipo_combustivel: str,
    quantidade,
    valor_total,
    horimetro=None,
    observacao: str = "",
) -> Abastecimento:
    """Registra um abastecimento e atualiza o horímetro da máquina se necessário."""
    try:
        maquina = Maquina.objects.get(id=maquina_id, owner=owner, is_active=True)
    except Maquina.DoesNotExist:
        raise ValidationError("Máquina inválida ou não encontrada.")

    try:
        safra = Safra.objects.get(id=safra_id, owner=owner)
    except Safra.DoesNotExist:
        raise ValidationError("Safra inválida ou não encontrada.")

    if not data:
        raise ValidationError("A data do abastecimento é obrigatória.")

    dec_quantidade = Decimal(str(quantidade))
    dec_valor_total = Decimal(str(valor_total))
    
    if dec_quantidade <= 0:
        raise ValidationError("A quantidade abastecida deve ser maior que zero.")
    if dec_valor_total <= 0:
        raise ValidationError("O valor total deve ser maior que zero.")

    dec_horimetro = None
    if horimetro is not None and horimetro != "":
        dec_horimetro = Decimal(str(horimetro))
        if dec_horimetro < maquina.horimetro_atual:
            raise ValidationError(
                f"O horímetro informado ({dec_horimetro}) não pode ser menor do que o atual da máquina ({maquina.horimetro_atual})."
            )
        # Atualiza o horímetro atual da máquina
        maquina.horimetro_atual = dec_horimetro
        maquina.save()

    abastecimento = Abastecimento(
        owner=owner,
        maquina=maquina,
        safra=safra,
        data=data,
        tipo_combustivel=tipo_combustivel,
        quantidade=dec_quantidade,
        valor_total=dec_valor_total,
        horimetro=dec_horimetro,
        observacao=observacao
    )
    abastecimento.full_clean()
    abastecimento.save()
    return abastecimento


def update_abastecimento(abastecimento: Abastecimento, **kwargs) -> Abastecimento:
    """Edita um abastecimento."""
    for key, val in kwargs.items():
        if val is not None:
            if key == "quantidade" or key == "valor_total":
                setattr(abastecimento, key, Decimal(str(val)))
            elif key == "horimetro" and val != "":
                dec_horimetro = Decimal(str(val))
                if dec_horimetro < abastecimento.maquina.horimetro_atual:
                    # Se for maior que o registrado mas menor que o atual da máquina,
                    # atualizamos se for o caso, mas deixamos passar ou validamos.
                    pass
                setattr(abastecimento, key, dec_horimetro)
            else:
                setattr(abastecimento, key, val)

    abastecimento.full_clean()
    abastecimento.save()
    return abastecimento


def delete_abastecimento(abastecimento: Abastecimento) -> None:
    """Exclui o abastecimento."""
    abastecimento.delete()


def create_uso_maquina(
    owner,
    maquina_id: int,
    talhao_id: int,
    safra_id: int,
    data,
    hora_inicio,
    hora_fim,
    horas_trabalhadas,
    atividade: str,
    operador: str = "",
    observacao: str = "",
) -> UsoMaquina:
    """Registra uso operacional de uma máquina e atualiza o horímetro."""
    try:
        maquina = Maquina.objects.get(id=maquina_id, owner=owner, is_active=True)
    except Maquina.DoesNotExist:
        raise ValidationError("Máquina inválida ou não encontrada.")

    try:
        talhao = Talhao.objects.get(id=talhao_id, propriedade__owner=owner)
    except Talhao.DoesNotExist:
        raise ValidationError("Talhão inválido ou não encontrado.")

    try:
        safra = Safra.objects.get(id=safra_id, owner=owner)
    except Safra.DoesNotExist:
        raise ValidationError("Safra inválida ou não encontrada.")

    dec_horas = Decimal(str(horas_trabalhadas))
    if dec_horas <= 0:
        raise ValidationError("As horas trabalhadas devem ser maiores que zero.")

    # Atualiza horímetro da máquina automaticamente!
    maquina.horimetro_atual += dec_horas
    maquina.save()

    uso = UsoMaquina(
        owner=owner,
        maquina=maquina,
        talhao=talhao,
        safra=safra,
        data=data,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        horas_trabalhadas=dec_horas,
        atividade=atividade,
        operador=operador,
        observacao=observacao
    )
    uso.full_clean()
    uso.save()
    return uso


def update_uso_maquina(uso: UsoMaquina, **kwargs) -> UsoMaquina:
    """Edita um uso de máquina."""
    old_horas = uso.horas_trabalhadas
    
    for key, val in kwargs.items():
        if val is not None:
            if key == "horas_trabalhadas":
                setattr(uso, key, Decimal(str(val)))
            else:
                setattr(uso, key, val)

    # Se horas foram atualizadas, compensar no horímetro da máquina
    if "horas_trabalhadas" in kwargs:
        diff_horas = uso.horas_trabalhadas - old_horas
        uso.maquina.horimetro_atual += diff_horas
        uso.maquina.save()

    uso.full_clean()
    uso.save()
    return uso


def delete_uso_maquina(uso: UsoMaquina) -> None:
    """Exclui uso de máquina e abate o horômetro correspondente."""
    maquina = uso.maquina
    maquina.horimetro_atual = max(Decimal("0.0"), maquina.horimetro_atual - uso.horas_trabalhadas)
    maquina.save()
    uso.delete()


def create_manutencao(
    owner,
    maquina_id: int,
    safra_id: int,
    tipo: str,
    data,
    descricao: str,
    custo,
    fornecedor: str = "",
    observacao: str = "",
) -> Manutencao:
    """Registra uma manutenção efetuada."""
    try:
        maquina = Maquina.objects.get(id=maquina_id, owner=owner, is_active=True)
    except Maquina.DoesNotExist:
        raise ValidationError("Máquina inválida ou não encontrada.")

    try:
        safra = Safra.objects.get(id=safra_id, owner=owner)
    except Safra.DoesNotExist:
        raise ValidationError("Safra inválida ou não encontrada.")

    dec_custo = Decimal(str(custo))
    if dec_custo < 0:
        raise ValidationError("O custo da manutenção não pode ser negativo.")

    manutencao = Manutencao(
        owner=owner,
        maquina=maquina,
        safra=safra,
        tipo=tipo,
        data=data,
        descricao=descricao,
        custo=dec_custo,
        fornecedor=fornecedor,
        observacao=observacao
    )
    manutencao.full_clean()
    manutencao.save()
    return manutencao


def update_manutencao(manutencao: Manutencao, **kwargs) -> Manutencao:
    """Edita registro de manutenção."""
    for key, val in kwargs.items():
        if val is not None:
            if key == "custo":
                setattr(manutencao, key, Decimal(str(val)))
            else:
                setattr(manutencao, key, val)
    
    manutencao.full_clean()
    manutencao.save()
    return manutencao


def delete_manutencao(manutencao: Manutencao) -> None:
    """Exclui registro de manutenção."""
    manutencao.delete()


def create_programacao_manutencao(
    owner,
    maquina_id: int,
    descricao: str,
    criterio: str,
    data_limite=None,
    horimetro_limite=None,
    dias_alerta: int = 15,
    horas_alerta=20.0,
) -> ProgramacaoManutencao:
    """Programa uma manutenção futura preventiva."""
    try:
        maquina = Maquina.objects.get(id=maquina_id, owner=owner, is_active=True)
    except Maquina.DoesNotExist:
        raise ValidationError("Máquina inválida ou não encontrada.")

    if not descricao:
        raise ValidationError("Descrição do serviço é obrigatória.")

    if criterio == "data" and not data_limite:
        raise ValidationError("Para critério por Data, a Data Limite é obrigatória.")
    if criterio == "horimetro" and horimetro_limite is None:
        raise ValidationError("Para critério por Horímetro, o Horímetro Limite é obrigatório.")

    dec_horimetro_limite = None
    if horimetro_limite is not None:
        dec_horimetro_limite = Decimal(str(horimetro_limite))

    programacao = ProgramacaoManutencao(
        owner=owner,
        maquina=maquina,
        descricao=descricao,
        criterio=criterio,
        data_limite=data_limite,
        horimetro_limite=dec_horimetro_limite,
        dias_alerta=dias_alerta,
        horas_alerta=Decimal(str(horas_alerta))
    )
    programacao.full_clean()
    programacao.save()
    return programacao


def update_programacao_manutencao(programacao: ProgramacaoManutencao, **kwargs) -> ProgramacaoManutencao:
    """Atualiza dados da programação de manutenção."""
    for key, val in kwargs.items():
        if val is not None:
            if key == "horimetro_limite" or key == "horas_alerta":
                setattr(programacao, key, Decimal(str(val)))
            else:
                setattr(programacao, key, val)

    programacao.full_clean()
    programacao.save()
    return programacao


def resolve_programacao_manutencao(programacao: ProgramacaoManutencao) -> None:
    """Marca a programação como resolvida/concluída."""
    programacao.concluida = True
    programacao.save()
