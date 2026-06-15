# apps/operational/web_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def operational_select_view(request):
    """Renderiza a página para o usuário selecionar a propriedade para o módulo operacional."""
    return render(request, "operational/operational_select.html", {"user": request.user})


@login_required
def operational_dashboard_view(request, propriedade_id):
    """Renderiza o dashboard operacional para uma propriedade específica."""
    return render(request, "operational/operational_dashboard.html", {
        "user": request.user,
        "propriedade_id": propriedade_id,
    })
