# apps/operational/web_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.properties.selectors import get_propriedades_by_user


@login_required
def operational_select_view(request):
    """Renderiza a página para o usuário selecionar a propriedade para o módulo operacional."""
    return render(request, "operational/operational_select.html", {"user": request.user})


@login_required
def operational_dashboard_view(request, propriedade_id):
    """Renderiza o dashboard operacional para uma propriedade específica."""
    user_properties = get_propriedades_by_user(user=request.user)
    propriedade_selecionada = user_properties.filter(id=propriedade_id).first()
    
    # Logs temporários solicitados
    prop_nome = propriedade_selecionada.nome if propriedade_selecionada else "Nenhuma/Inválida"
    url_final = f"/operacional/{propriedade_id}/"
    print(f"[Operacional Web View] Propriedade selecionada: {prop_nome} | ID enviado para a rota: {propriedade_id} | URL final gerada: {url_final}")
    
    if not propriedade_selecionada:
        # Se a propriedade não pertencer ao usuário, redireciona para a seleção de propriedades
        return redirect("web_operational:select")

    return render(request, "operational/operational_dashboard.html", {
        "user": request.user,
        "propriedade_id": propriedade_id,
    })

