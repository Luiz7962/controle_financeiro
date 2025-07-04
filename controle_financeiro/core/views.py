from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum
from .models import Transacao
from .forms import TransacaoForm
from decimal import Decimal

# Imports para geração de gráficos
import matplotlib.pyplot as plt
import io
import base64

# --- Views de Autenticação (sem alterações) ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Views de Transação (sem alterações) ---
@login_required
def index(request):
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.user = request.user
            transacao.save()
            return redirect('index')
    else:
        form = TransacaoForm()
    transacoes = Transacao.objects.filter(user=request.user)
    saldo_total = Decimal('0.00')
    for transacao in transacoes:
        if transacao.tipo == 'Receita':
            saldo_total += transacao.valor
        else:
            saldo_total -= transacao.valor
    context = {
        'transacoes': transacoes,
        'form': form,
        'saldo_total': saldo_total,
    }
    return render(request, 'core/index.html', context)

@login_required
def edit_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransacaoForm(request.POST, instance=transacao)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TransacaoForm(instance=transacao)
    context = {
        'form': form,
        'transacao': transacao
    }
    return render(request, 'core/edit_transacao.html', context)

@login_required
def delete_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    if request.method == 'POST':
        transacao.delete()
        return redirect('index')
    context = {
        'transacao': transacao
    }
    return render(request, 'core/delete_confirm.html', context)

# --- NOVA VIEW DE RELATÓRIOS ---
@login_required
def relatorios(request):
    """
    Gera e exibe um relatório de despesas por categoria.
    """
    # 1. Filtra as despesas do usuário logado
    despesas = Transacao.objects.filter(user=request.user, tipo='Despesa')
    
    # 2. Agrupa por categoria e soma os valores
    # O resultado será um QuerySet de dicionários, ex: [{'categoria': 'Lazer', 'total': 150.00}, ...]
    gastos_por_categoria = despesas.values('categoria').annotate(total=Sum('valor')).order_by('-total')

    # 3. Prepara os dados para o gráfico
    categorias = [item['categoria'] for item in gastos_por_categoria]
    totais = [item['total'] for item in gastos_por_categoria]

    # 4. Gera o gráfico com Matplotlib
    plt.switch_backend('Agg') # Necessário para rodar em um servidor sem interface gráfica
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(categorias, totais, color='#4F46E5') # Gráfico de barras horizontais
    ax.set_title('Gastos por Categoria', fontsize=16)
    ax.set_xlabel('Total Gasto (R$)')
    ax.invert_yaxis() # A categoria com maior gasto fica no topo
    plt.tight_layout()

    # 5. Converte o gráfico para uma imagem em memória
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Codifica a imagem em base64 para embutir no HTML
    imagem_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    context = {
        'gastos_por_categoria': gastos_por_categoria,
        'grafico': imagem_base64,
    }
    return render(request, 'core/relatorios.html', context)
