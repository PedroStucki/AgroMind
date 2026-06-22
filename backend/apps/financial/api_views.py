# apps/financial/api_views.py
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.properties.selectors import get_propriedades_by_user
from .models import Despesa, Receita
from .serializers import DespesaSerializer, ReceitaSerializer
from .selectors import get_consolidado_financeiro, get_fluxo_caixa_cronologico


class FinancialBaseMixin:
    """Mixin para garantir que as operações sejam limitadas à propriedade e ao usuário."""
    
    def get_propriedade(self):
        propriedade_id = self.kwargs.get("propriedade_id")
        prop = get_propriedades_by_user(self.request.user).filter(id=propriedade_id).first()
        return prop

    def get_queryset(self):
        prop = self.get_propriedade()
        if not prop:
            return self.queryset.none()
        
        qs = self.queryset.filter(owner=self.request.user, propriedade=prop)
        
        # Filtros básicos
        safra_id = self.request.query_params.get("safra_id")
        if safra_id:
            qs = qs.filter(safra_id=safra_id)
            
        data_inicio = self.request.query_params.get("data_inicio")
        if data_inicio:
            if hasattr(self.queryset.model, "data_venda"):
                qs = qs.filter(data_venda__gte=data_inicio)
            else:
                qs = qs.filter(data__gte=data_inicio)
                
        data_fim = self.request.query_params.get("data_fim")
        if data_fim:
            if hasattr(self.queryset.model, "data_venda"):
                qs = qs.filter(data_venda__lte=data_fim)
            else:
                qs = qs.filter(data__lte=data_fim)
                
        return qs

    def perform_create(self, serializer):
        prop = self.get_propriedade()
        serializer.save(owner=self.request.user, propriedade=prop)


class DespesaViewSet(FinancialBaseMixin, viewsets.ModelViewSet):
    queryset = Despesa.objects.all()
    serializer_class = DespesaSerializer
    permission_classes = [IsAuthenticated]


class ReceitaViewSet(FinancialBaseMixin, viewsets.ModelViewSet):
    queryset = Receita.objects.all()
    serializer_class = ReceitaSerializer
    permission_classes = [IsAuthenticated]


class ConsolidadoFinanceiroAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, propriedade_id):
        prop = get_propriedades_by_user(request.user).filter(id=propriedade_id).first()
        if not prop:
            return Response({"detail": "Propriedade não encontrada."}, status=404)
        
        safra_id = request.query_params.get("safra_id")
        if safra_id:
            safra_id = int(safra_id)
            
        dados = get_consolidado_financeiro(request.user, propriedade_id, safra_id)
        return Response(dados)


class FluxoCaixaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, propriedade_id):
        prop = get_propriedades_by_user(request.user).filter(id=propriedade_id).first()
        if not prop:
            return Response({"detail": "Propriedade não encontrada."}, status=404)
        
        safra_id = request.query_params.get("safra_id")
        if safra_id:
            safra_id = int(safra_id)
            
        fluxo = get_fluxo_caixa_cronologico(request.user, propriedade_id, safra_id)
        return Response(fluxo)
