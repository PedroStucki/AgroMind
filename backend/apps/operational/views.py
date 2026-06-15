# apps/operational/views.py
# Python 3.12+ | Django 5.x

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.properties.selectors import get_propriedade_by_id
from . import selectors, services
from .serializers import (
    MaquinaSerializer, MaquinaCreateSerializer, MaquinaUpdateSerializer,
    AbastecimentoSerializer, AbastecimentoCreateSerializer, AbastecimentoUpdateSerializer,
    UsoMaquinaSerializer, UsoMaquinaCreateSerializer, UsoMaquinaUpdateSerializer,
    ManutencaoSerializer, ManutencaoCreateSerializer, ManutencaoUpdateSerializer,
    ProgramacaoManutencaoSerializer, ProgramacaoCreateSerializer, ProgramacaoUpdateSerializer,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_prop_or_404(propriedade_id, user):
    try:
        return get_propriedade_by_id(propriedade_id=propriedade_id, user=user)
    except Exception:
        return None


def _error(detail, code=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": detail}, status=code)


# ── Máquinas CRUD ─────────────────────────────────────────────────────────────

class MaquinaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        maquinas = selectors.get_maquinas_by_propriedade(request.user, propriedade_id)
        return Response(MaquinaSerializer(maquinas, many=True).data)

    def post(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = MaquinaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            maquina = services.create_maquina(
                owner=request.user,
                propriedade_id=propriedade_id,
                **serializer.validated_data,
            )
        except ValidationError as e:
            return _error(e.messages)
        return Response(MaquinaSerializer(maquina).data, status=status.HTTP_201_CREATED)


class MaquinaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, maquina_id):
        try:
            return selectors.get_maquina_by_id(request.user, maquina_id)
        except Exception:
            return None

    def get(self, request: Request, propriedade_id: int, maquina_id: int) -> Response:
        maquina = self._get(request, maquina_id)
        if not maquina or maquina.propriedade_id != propriedade_id:
            return _error("Máquina não encontrada.", status.HTTP_404_NOT_FOUND)
        return Response(MaquinaSerializer(maquina).data)

    def patch(self, request: Request, propriedade_id: int, maquina_id: int) -> Response:
        maquina = self._get(request, maquina_id)
        if not maquina or maquina.propriedade_id != propriedade_id:
            return _error("Máquina não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = MaquinaUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            maquina = services.update_maquina(maquina=maquina, **serializer.validated_data)
        except ValidationError as e:
            return _error(e.messages)
        return Response(MaquinaSerializer(maquina).data)

    def delete(self, request: Request, propriedade_id: int, maquina_id: int) -> Response:
        maquina = self._get(request, maquina_id)
        if not maquina or maquina.propriedade_id != propriedade_id:
            return _error("Máquina não encontrada.", status.HTTP_404_NOT_FOUND)
        services.deactivate_maquina(maquina)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MaquinaHistoricoView(APIView):
    """RF-28 — Histórico completo de ciclo de vida de um equipamento."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int, maquina_id: int) -> Response:
        try:
            historico = selectors.get_historico_maquina(request.user, maquina_id)
        except Exception:
            return _error("Máquina não encontrada.", status.HTTP_404_NOT_FOUND)
        return Response(historico)


# ── Abastecimentos ────────────────────────────────────────────────────────────

class AbastecimentoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        qs = selectors.get_abastecimentos_by_propriedade(
            owner=request.user,
            propriedade_id=propriedade_id,
            maquina_id=request.query_params.get("maquina_id"),
            safra_id=request.query_params.get("safra_id"),
            data_inicio=request.query_params.get("data_inicio"),
            data_fim=request.query_params.get("data_fim"),
        )
        return Response(AbastecimentoSerializer(qs, many=True).data)

    def post(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = AbastecimentoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            abast = services.create_abastecimento(
                owner=request.user,
                maquina_id=d["maquina_id"],
                safra_id=d["safra_id"],
                data=d["data"],
                tipo_combustivel=d["tipo_combustivel"],
                quantidade=d["quantidade"],
                valor_total=d["valor_total"],
                horimetro=d.get("horimetro"),
                observacao=d.get("observacao", ""),
            )
        except ValidationError as e:
            return _error(e.messages)
        return Response(AbastecimentoSerializer(abast).data, status=status.HTTP_201_CREATED)


class AbastecimentoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, abastecimento_id):
        try:
            from .models import Abastecimento
            return Abastecimento.objects.get(id=abastecimento_id, owner=request.user)
        except Exception:
            return None

    def get(self, request: Request, propriedade_id: int, abastecimento_id: int) -> Response:
        obj = self._get(request, abastecimento_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Abastecimento não encontrado.", status.HTTP_404_NOT_FOUND)
        return Response(AbastecimentoSerializer(obj).data)

    def patch(self, request: Request, propriedade_id: int, abastecimento_id: int) -> Response:
        obj = self._get(request, abastecimento_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Abastecimento não encontrado.", status.HTTP_404_NOT_FOUND)
        serializer = AbastecimentoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = services.update_abastecimento(obj, **serializer.validated_data)
        except ValidationError as e:
            return _error(e.messages)
        return Response(AbastecimentoSerializer(obj).data)

    def delete(self, request: Request, propriedade_id: int, abastecimento_id: int) -> Response:
        obj = self._get(request, abastecimento_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Abastecimento não encontrado.", status.HTTP_404_NOT_FOUND)
        services.delete_abastecimento(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Uso de Máquinas ───────────────────────────────────────────────────────────

class UsoMaquinaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        qs = selectors.get_usos_by_propriedade(
            owner=request.user,
            propriedade_id=propriedade_id,
            maquina_id=request.query_params.get("maquina_id"),
            safra_id=request.query_params.get("safra_id"),
            talhao_id=request.query_params.get("talhao_id"),
            data_inicio=request.query_params.get("data_inicio"),
            data_fim=request.query_params.get("data_fim"),
        )
        return Response(UsoMaquinaSerializer(qs, many=True).data)

    def post(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = UsoMaquinaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            uso = services.create_uso_maquina(
                owner=request.user,
                maquina_id=d["maquina_id"],
                talhao_id=d["talhao_id"],
                safra_id=d["safra_id"],
                data=d["data"],
                hora_inicio=d["hora_inicio"],
                hora_fim=d["hora_fim"],
                horas_trabalhadas=d["horas_trabalhadas"],
                atividade=d["atividade"],
                operador=d.get("operador", ""),
                observacao=d.get("observacao", ""),
            )
        except ValidationError as e:
            return _error(e.messages)
        return Response(UsoMaquinaSerializer(uso).data, status=status.HTTP_201_CREATED)


class UsoMaquinaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, uso_id):
        try:
            from .models import UsoMaquina
            return UsoMaquina.objects.get(id=uso_id, owner=request.user)
        except Exception:
            return None

    def get(self, request: Request, propriedade_id: int, uso_id: int) -> Response:
        obj = self._get(request, uso_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Uso de máquina não encontrado.", status.HTTP_404_NOT_FOUND)
        return Response(UsoMaquinaSerializer(obj).data)

    def patch(self, request: Request, propriedade_id: int, uso_id: int) -> Response:
        obj = self._get(request, uso_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Uso de máquina não encontrado.", status.HTTP_404_NOT_FOUND)
        serializer = UsoMaquinaUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = services.update_uso_maquina(obj, **serializer.validated_data)
        except ValidationError as e:
            return _error(e.messages)
        return Response(UsoMaquinaSerializer(obj).data)

    def delete(self, request: Request, propriedade_id: int, uso_id: int) -> Response:
        obj = self._get(request, uso_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Uso de máquina não encontrado.", status.HTTP_404_NOT_FOUND)
        services.delete_uso_maquina(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Manutenções ───────────────────────────────────────────────────────────────

class ManutencaoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        qs = selectors.get_manutencoes_by_propriedade(
            owner=request.user,
            propriedade_id=propriedade_id,
            maquina_id=request.query_params.get("maquina_id"),
            safra_id=request.query_params.get("safra_id"),
            tipo=request.query_params.get("tipo"),
            data_inicio=request.query_params.get("data_inicio"),
            data_fim=request.query_params.get("data_fim"),
        )
        return Response(ManutencaoSerializer(qs, many=True).data)

    def post(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = ManutencaoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            manut = services.create_manutencao(
                owner=request.user,
                maquina_id=d["maquina_id"],
                safra_id=d["safra_id"],
                tipo=d["tipo"],
                data=d["data"],
                descricao=d["descricao"],
                custo=d["custo"],
                fornecedor=d.get("fornecedor", ""),
                observacao=d.get("observacao", ""),
            )
        except ValidationError as e:
            return _error(e.messages)
        return Response(ManutencaoSerializer(manut).data, status=status.HTTP_201_CREATED)


class ManutencaoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, manutencao_id):
        try:
            from .models import Manutencao
            return Manutencao.objects.get(id=manutencao_id, owner=request.user)
        except Exception:
            return None

    def get(self, request: Request, propriedade_id: int, manutencao_id: int) -> Response:
        obj = self._get(request, manutencao_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Manutenção não encontrada.", status.HTTP_404_NOT_FOUND)
        return Response(ManutencaoSerializer(obj).data)

    def patch(self, request: Request, propriedade_id: int, manutencao_id: int) -> Response:
        obj = self._get(request, manutencao_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Manutenção não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = ManutencaoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = services.update_manutencao(obj, **serializer.validated_data)
        except ValidationError as e:
            return _error(e.messages)
        return Response(ManutencaoSerializer(obj).data)

    def delete(self, request: Request, propriedade_id: int, manutencao_id: int) -> Response:
        obj = self._get(request, manutencao_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Manutenção não encontrada.", status.HTTP_404_NOT_FOUND)
        services.delete_manutencao(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Programações de Manutenção ────────────────────────────────────────────────

class ProgramacaoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        concluida = request.query_params.get("concluida", "false").lower() == "true"
        qs = selectors.get_programacoes_by_propriedade(
            owner=request.user,
            propriedade_id=propriedade_id,
            maquina_id=request.query_params.get("maquina_id"),
            concluida=concluida,
        )
        return Response(ProgramacaoManutencaoSerializer(qs, many=True).data)

    def post(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = ProgramacaoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            prog = services.create_programacao_manutencao(
                owner=request.user,
                maquina_id=d["maquina_id"],
                descricao=d["descricao"],
                criterio=d["criterio"],
                data_limite=d.get("data_limite"),
                horimetro_limite=d.get("horimetro_limite"),
                dias_alerta=d.get("dias_alerta", 15),
                horas_alerta=d.get("horas_alerta", 20.0),
            )
        except ValidationError as e:
            return _error(e.messages)
        return Response(ProgramacaoManutencaoSerializer(prog).data, status=status.HTTP_201_CREATED)


class ProgramacaoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, prog_id):
        try:
            from .models import ProgramacaoManutencao
            return ProgramacaoManutencao.objects.get(id=prog_id, owner=request.user)
        except Exception:
            return None

    def patch(self, request: Request, propriedade_id: int, prog_id: int) -> Response:
        obj = self._get(request, prog_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Programação não encontrada.", status.HTTP_404_NOT_FOUND)
        serializer = ProgramacaoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = services.update_programacao_manutencao(obj, **serializer.validated_data)
        except ValidationError as e:
            return _error(e.messages)
        return Response(ProgramacaoManutencaoSerializer(obj).data)

    def delete(self, request: Request, propriedade_id: int, prog_id: int) -> Response:
        obj = self._get(request, prog_id)
        if not obj or obj.maquina.propriedade_id != propriedade_id:
            return _error("Programação não encontrada.", status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProgramacaoResolverView(APIView):
    """Marca uma programação de manutenção como concluída."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, propriedade_id: int, prog_id: int) -> Response:
        try:
            from .models import ProgramacaoManutencao
            obj = ProgramacaoManutencao.objects.get(id=prog_id, owner=request.user)
        except Exception:
            return _error("Programação não encontrada.", status.HTTP_404_NOT_FOUND)
        if obj.maquina.propriedade_id != propriedade_id:
            return _error("Programação não encontrada.", status.HTTP_404_NOT_FOUND)
        services.resolve_programacao_manutencao(obj)
        return Response({"detail": "Manutenção marcada como concluída."})


# ── Alertas e Consolidado ─────────────────────────────────────────────────────

class AlertasManutencaoView(APIView):
    """RF-25 — Alertas de manutenções próximas ao vencimento."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        alertas = selectors.get_alertas_manutencao(request.user, propriedade_id)
        return Response(alertas)


class ConsolidadoCustosView(APIView):
    """RF-27 — Consolidação automática de custos operacionais."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, propriedade_id: int) -> Response:
        if not _get_prop_or_404(propriedade_id, request.user):
            return _error("Propriedade não encontrada.", status.HTTP_404_NOT_FOUND)
        consolidado = selectors.get_consolidado_custos(
            owner=request.user,
            propriedade_id=propriedade_id,
            safra_id=request.query_params.get("safra_id"),
            talhao_id=request.query_params.get("talhao_id"),
            cultura=request.query_params.get("cultura"),
            data_inicio=request.query_params.get("data_inicio"),
            data_fim=request.query_params.get("data_fim"),
        )
        return Response(consolidado)
