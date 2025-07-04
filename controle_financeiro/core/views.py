from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum
from .models import Transacao
from .forms import TransacaoForm
from decimal import Decimal
from datetime import datetime # Importe o datetime

# Imports para geração de gráficos
import matplotlib.pyplot as plt
import io
import base64

# --- Views de Autenticação e Transação (sem alterações) ---
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

# --- VIEW DE RELATÓRIOS ATUALIZADA COM FILTROS ---
@login_required
def relatorios(request):
    """
    Gera e exibe um relatório de despesas por categoria, com filtros por mês e ano.
    """
    # 1. Obter o ano e mês atuais como padrão
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month

    # 2. Obter os valores do filtro do formulário (se existirem)
    ano_selecionado = request.GET.get('ano', ano_atual)
    mes_selecionado = request.GET.get('mes', mes_atual)

    # 3. Filtrar as despesas do usuário pelo ano e mês selecionados
    despesas = Transacao.objects.filter(
        user=request.user, 
        tipo='Despesa',
        data__year=ano_selecionado,
        data__month=mes_selecionado
    )
    
    # 4. Agrupar por categoria e somar os valores
    gastos_por_categoria = despesas.values('categoria').annotate(total=Sum('valor')).order_by('-total')

    # 5. Preparar dados para o gráfico
    categorias = [item['categoria'] for item in gastos_por_categoria]
    totais = [float(item['total']) for item in gastos_por_categoria] # Converter Decimal para float para o gráfico

    grafico = None
    if totais:
        # 6. Gerar o gráfico com Matplotlib
        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(categorias, totais, color='#4F46E5')
        ax.set_title(f'Gastos por Categoria - {mes_selecionado}/{ano_selecionado}', fontsize=16)
        ax.set_xlabel('Total Gasto (R$)')
        ax.invert_yaxis()
        plt.tight_layout()

        # 7. Converter o gráfico para uma imagem em memória
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        imagem_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        grafico = imagem_base64

    # Criar lista de anos para o dropdown (desde o primeiro registro até o ano atual)
    primeiro_ano = Transacao.objects.filter(user=request.user).order_by('data').first()
    anos_disponiveis = range(primeiro_ano.data.year, ano_atual + 1) if primeiro_ano else [ano_atual]
    
    context = {
        'gastos_por_categoria': gastos_por_categoria,
        'grafico': grafico,
        'anos': anos_disponiveis,
        'ano_selecionado': int(ano_selecionado),
        'mes_selecionado': int(mes_selecionado),
    }
    return render(request, 'core/relatorios.html', context)
