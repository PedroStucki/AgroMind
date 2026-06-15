# apps/planting/api_views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Safra


class SafraListView(APIView):
    """Lista safras de uma propriedade específica (usado por outros módulos)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, propriedade_id):
        safras = Safra.objects.filter(
            owner=request.user,
            propriedade_id=propriedade_id,
        ).order_by("-data_inicio")
        data = [
            {
                "id": s.id,
                "nome": s.nome,
                "cultura": s.cultura,
                "data_inicio": s.data_inicio.isoformat(),
                "data_fim": s.data_fim.isoformat() if s.data_fim else None,
            }
            for s in safras
        ]
        return Response(data)
