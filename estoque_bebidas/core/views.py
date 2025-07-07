from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, F, Q
from .models import *
from .forms import *
from django.http import JsonResponse

# Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciais inválidas.')
    return render(request, 'login.html')

# Logout
def user_logout(request):
    logout(request)
    return redirect('login')

# Registro
def register(request):
    if request.method == 'POST':
        form = UsuárioRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário registrado com sucesso!')
            return redirect('login')
    else:
        form = UsuárioRegisterForm()
    return render(request, 'register.html', {'form': form})

# Dashboard
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# Cadastro de Fornecedores
@login_required
def fornecedor_create(request):
    if request.user.papel not in ['Proprietario', 'Gerente']:
        messages.error(request, 'Permissão negada.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('fornecedor_list')
    else:
        form = FornecedorForm()
    return render(request, 'fornecedor_form.html', {'form': form})

# Lista de Fornecedores
@login_required
def fornecedor_list(request):
    query = request.GET.get('q', '')
    fornecedores = []
    if query:
        fornecedores = Fornecedor.objects.filter(
            Q(nome__icontains=query) | Q(contato__icontains=query) | Q(endereco__icontains=query)
        )
    return render(request, 'fornecedor_list.html', {'fornecedores': fornecedores, 'query': query})

# Cadastro de Produtos
@login_required
def produto_create(request):
    if request.user.papel not in ['Proprietario', 'Gerente']:
        messages.error(request, 'Permissão negada.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            if Produto.objects.filter(nome=produto.nome).exists():
                messages.error(request, 'Já existe um produto com este nome.')
                return render(request, 'produto_form.html', {'form': form})
            produto.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produto_list')
    else:
        form = ProdutoForm()
    return render(request, 'produto_form.html', {'form': form})

# Lista de Produtos
@login_required
def produto_list(request):
    query = request.GET.get('q', '')
    produtos = []
    if query:
        produtos = Produto.objects.filter(
            Q(nome__icontains=query) | Q(categoria__icontains=query) | Q(volumetria__icontains=query) |
            Q(lotes__numero_lote__icontains=query)
        ).distinct()
    return render(request, 'produto_list.html', {'produtos': produtos, 'query': query})

@login_required
def movimentação_estoque_create(request):
    if request.method == 'POST':
        print(f"Dados recebidos: {request.POST}")  # Depuração
        form = MovimentaçãoEstoqueForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.id_usuário = request.user
            tipo_movimentacao = form.cleaned_data['tipo_movimentacao']
            numero_lote = form.cleaned_data['numero_lote']
            data_validade = form.cleaned_data['data_validade']
            id_lote = form.cleaned_data['id_lote']
            produto = form.cleaned_data['produto']

            try:
                if tipo_movimentacao == 'Entrada':
                    if not numero_lote or not data_validade:
                        messages.error(request, 'Número do lote e data de validade são obrigatórios para entradas.')
                        return render(request, 'movimentação_estoque_form.html', {'form': form})
                    lote, created = Lote.objects.get_or_create(
                        id_produto=produto,
                        numero_lote=numero_lote,
                        defaults={'data_validade': data_validade, 'quantidade': 0}
                    )
                    if not created and lote.data_validade != data_validade:
                        messages.error(request, 'Já existe um lote com este número, mas com data de validade diferente.')
                        return render(request, 'movimentação_estoque_form.html', {'form': form})
                    lote.quantidade += movement.quantidade
                    produto.estoque_atual += movement.quantidade
                else:
                    if not id_lote:
                        messages.error(request, 'Selecione um lote válido para saídas ou ajustes.')
                        return render(request, 'movimentação_estoque_form.html', {'form': form})
                    lote = id_lote
                    if lote.id_produto != produto:
                        messages.error(request, 'O lote selecionado não pertence ao produto escolhido.')
                        return render(request, 'movimentação_estoque_form.html', {'form': form})
                    if tipo_movimentacao == 'Saida':
                        if lote.quantidade < movement.quantidade:
                            messages.error(request, 'Estoque insuficiente para o lote selecionado.')
                            return render(request, 'movimentação_estoque_form.html', {'form': form})
                        lote.quantidade -= movement.quantidade
                        produto.estoque_atual -= movement.quantidade
                    elif tipo_movimentacao == 'Ajuste':
                        produto.estoque_atual = produto.estoque_atual - lote.quantidade + movement.quantidade
                        lote.quantidade = movement.quantidade

                lote.save()
                produto.save()
                movement.id_lote = lote
                movement.save()
                messages.success(request, 'Movimentação registrada com sucesso!')
                return redirect('movimentação_estoque_list')
            except Exception as e:
                messages.error(request, f'Erro ao salvar movimentação: {str(e)}')
                print(f"Erro ao salvar: {str(e)}")  # Depuração
                return render(request, 'movimentação_estoque_form.html', {'form': form})
        else:
            messages.error(request, 'Erro no formulário. Verifique os campos.')
            print(f"Erros do formulário: {form.errors}")  # Depuração
    else:
        form = MovimentaçãoEstoqueForm()
    return render(request, 'movimentação_estoque_form.html', {'form': form})

@login_required
def get_lotes(request):
    produto_id = request.GET.get('produto_id')
    try:
        lotes = Lote.objects.filter(id_produto_id=produto_id).values('id_lote', 'numero_lote', 'data_validade')
        print(f"Produto ID: {produto_id}, Lotes encontrados: {list(lotes)}")  # Depuração
        return JsonResponse({'lotes': list(lotes)})
    except Exception as e:
        print(f"Erro em get_lotes: {str(e)}")  # Depuração
        return JsonResponse({'lotes': []}, status=400)

# Lista de Movimentações
@login_required
def movimentação_estoque_list(request):
    query = request.GET.get('q', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    filtros = Q()
    if query:
        filtros &= (
            Q(id_lote__id_produto__nome__icontains=query) |
            Q(tipo_movimentacao__icontains=query) |
            Q(motivo__icontains=query) |
            Q(id_usuário__username__icontains=query) |
            Q(id_lote__numero_lote__icontains=query)
        )
    if data_inicio:
        filtros &= Q(data_movimentacao__date__gte=data_inicio)
    if data_fim:
        filtros &= Q(data_movimentacao__date__lte=data_fim)

    if filtros:
        movimentações = MovimentaçãoEstoque.objects.filter(filtros).order_by('-data_movimentacao')
    else:
        movimentações = MovimentaçãoEstoque.objects.all().order_by('-data_movimentacao')

    return render(request, 'movimentação_estoque_list.html', {
        'movimentações': movimentações,
        'query': query,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })

# Relatório de Estoque Atual
@login_required
def stock_report(request):
    lotes = Lote.objects.select_related('id_produto').all()
    return render(request, 'stock_report.html', {'lotes': lotes})

# Relatório de Produtos em Nível Crítico
@login_required
def critical_stock_report(request):
    lotes = Lote.objects.select_related('id_produto').filter(
        quantidade__lte=F('id_produto__estoque_minimo')
    )
    return render(request, 'critical_stock_report.html', {'lotes': lotes})

@login_required
def abc_curve_report(request):
    # Agrupar movimentações por produto, somando as quantidades
    movimentações = MovimentaçãoEstoque.objects.values('id_lote__id_produto').annotate(
        total_movimentado=Sum('quantidade')
    ).order_by('-total_movimentado')

    total_geral = sum(item['total_movimentado'] for item in movimentações)
    produtos_abc = []
    acumulado = 0
    for item in movimentações:
        produto = Produto.objects.get(id_produto=item['id_lote__id_produto'])
        quantidade = item['total_movimentado']
        percentual = (quantidade / total_geral * 100) if total_geral > 0 else 0
        acumulado += percentual

        if acumulado <= 80:
            categoria_abc = 'A'
        elif acumulado <= 95:
            categoria_abc = 'B'
        else:
            categoria_abc = 'C'

        produtos_abc.append({
            'produto': produto,
            'total_movimentado': quantidade,
            'percentual': percentual,
            'categoria_abc': categoria_abc
        })

    return render(request, 'abc_curve_report.html', {'produtos_abc': produtos_abc})

# Função para alerta de estoque crítico
def send_critical_stock_alert():
    lotes = Lote.objects.select_related('id_produto').filter(
        quantidade__lte=F('id_produto__estoque_minimo')
    )
    for lote in lotes:
        print(f"Alerta: Estoque crítico para {lote.id_produto.nome} (Lote: {lote.numero_lote}) - Estoque atual: {lote.quantidade}")