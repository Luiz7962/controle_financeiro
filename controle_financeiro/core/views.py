from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib import messages # Importe o messages framework
from .models import Transacao
from .forms import TransacaoForm
from decimal import Decimal
from datetime import datetime
import json

# --- Views de Autenticação e outras (sem alterações) ---
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
def relatorios(request):
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    ano_selecionado = request.GET.get('ano', ano_atual)
    mes_selecionado = request.GET.get('mes', mes_atual)
    despesas = Transacao.objects.filter(
        user=request.user, 
        tipo='Despesa',
        data__year=ano_selecionado,
        data__month=mes_selecionado
    )
    gastos_por_categoria = despesas.values('categoria').annotate(total=Sum('valor')).order_by('-total')
    categorias = [item['categoria'] for item in gastos_por_categoria]
    totais = [float(item['total']) for item in gastos_por_categoria]
    categorias_json = json.dumps(categorias)
    totais_json = json.dumps(totais)
    primeiro_ano = Transacao.objects.filter(user=request.user).order_by('data').first()
    anos_disponiveis = range(primeiro_ano.data.year, ano_atual + 1) if primeiro_ano else [ano_atual]
    context = {
        'gastos_por_categoria': gastos_por_categoria,
        'categorias_json': categorias_json,
        'totais_json': totais_json,
        'anos': anos_disponiveis,
        'ano_selecionado': int(ano_selecionado),
        'mes_selecionado': int(mes_selecionado),
        'periodo_selecionado': f'{int(mes_selecionado):02d}/{ano_selecionado}'
    }
    return render(request, 'core/relatorios.html', context)

# --- VIEWS DE AÇÃO ATUALIZADAS COM MENSAGENS ---

@login_required
def index(request):
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.user = request.user
            transacao.save()
            # Adiciona uma mensagem de sucesso
            messages.success(request, 'Transação adicionada com sucesso!')
            return redirect('index')
    else:
        form = TransacaoForm()

    lista_transacoes = Transacao.objects.filter(user=request.user)
    paginador = Paginator(lista_transacoes, 10)
    numero_pagina = request.GET.get('page')
    transacoes_pagina = paginador.get_page(numero_pagina)

    saldo_total = Decimal('0.00')
    for transacao in lista_transacoes:
        if transacao.tipo == 'Receita':
            saldo_total += transacao.valor
        else:
            saldo_total -= transacao.valor
            
    context = {
        'transacoes': transacoes_pagina,
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
            # Adiciona uma mensagem de sucesso
            messages.success(request, 'Transação atualizada com sucesso!')
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
        # Adiciona uma mensagem de sucesso
        messages.success(request, 'Transação apagada com sucesso!')
        return redirect('index')
    
    context = {
        'transacao': transacao
    }
    return render(request, 'core/delete_confirm.html', context)
