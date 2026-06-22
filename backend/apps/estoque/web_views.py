# apps/estoque/web_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def estoque_select_view(request):
    """Renderiza a página para o usuário selecionar de qual propriedade quer ver o estoque."""
    return render(request, "estoque/estoque_select.html", {"user": request.user})

@login_required
def estoque_dashboard_view(request, propriedade_id):
    """Renderiza o dashboard de estoque para uma propriedade específica."""
    return render(request, "estoque/estoque_dashboard.html", {
        "user": request.user,
        "propriedade_id": propriedade_id
    })


@login_required
def estoque_historico_view(request, propriedade_id, insumo_id):
    """Renderiza a página de histórico/rastreabilidade de um insumo específico."""
    return render(request, "estoque/estoque_historico.html", {
        "user": request.user,
        "propriedade_id": propriedade_id,
        "insumo_id": insumo_id
    })
