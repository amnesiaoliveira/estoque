from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, F, Q
from .models import *
from .forms import *
from django.http import JsonResponse
from datetime import date, timedelta

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

def user_logout(request):
    logout(request)
    return redirect('login')

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

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

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

@login_required
def fornecedor_edit(request, id_fornecedor):
    if request.user.papel not in ['Proprietario', 'Gerente']:
        messages.error(request, 'Permissão negada.')
        return redirect('dashboard')
    fornecedor = get_object_or_404(Fornecedor, id_fornecedor=id_fornecedor)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor atualizado com sucesso!')
            return redirect('fornecedor_list')
    else:
        form = FornecedorForm(instance=fornecedor)
    return render(request, 'fornecedor_form.html', {'form': form, 'fornecedor': fornecedor})

@login_required
def fornecedor_list(request):
    query = request.GET.get('q', '')
    fornecedores = Fornecedor.objects.filter(
        Q(nome__icontains=query) | Q(contato__icontains=query) | Q(endereco__icontains=query)
    ).order_by('nome')
    return render(request, 'fornecedor_list.html', {'fornecedores': fornecedores, 'query': query})

@login_required
def produto_create(request):
    if request.user.papel not in ['Proprietario', 'Gerente']:
        messages.error(request, 'Permissão negada.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            if Produto.objects.filter(nome=produto.nome).exclude(id_produto=produto.id_produto).exists():
                messages.error(request, 'Já existe um produto com este nome.')
                return render(request, 'produto_form.html', {'form': form})
            produto.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produto_list')
    else:
        form = ProdutoForm()
    return render(request, 'produto_form.html', {'form': form})

@login_required
def produto_edit(request, id_produto):
    if request.user.papel not in ['Proprietario', 'Gerente']:
        messages.error(request, 'Permissão negada.')
        return redirect('dashboard')
    produto = get_object_or_404(Produto, id_produto=id_produto)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            produto = form.save(commit=False)
            if Produto.objects.filter(nome=produto.nome).exclude(id_produto=produto.id_produto).exists():
                messages.error(request, 'Já existe um produto com este nome.')
                return render(request, 'produto_form.html', {'form': form})
            produto.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('produto_list')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'produto_form.html', {'form': form, 'produto': produto})

@login_required
def produto_list(request):
    query = request.GET.get('q', '')
    produtos = Produto.objects.filter(
        Q(nome__icontains=query) | Q(categoria__icontains=query) | Q(volumetria__icontains=query) |
        Q(lotes__numero_lote__icontains=query)
    ).distinct().order_by('nome')
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

@login_required
def stock_report(request):
    query = request.GET.get('q', '')

    # Filtrar lotes por nome do produto
    lotes = Lote.objects.select_related('id_produto').filter(
        Q(id_produto__nome__icontains=query)
    ).order_by('id_produto__nome', 'numero_lote')

    return render(request, 'stock_report.html', {
        'lotes': lotes,
        'query': query
    })

@login_required
def critical_stock_report(request):
    query = request.GET.get('q', '')

    # Filtrar lotes por nome do produto e estoque crítico
    lotes = Lote.objects.select_related('id_produto').filter(
        Q(id_produto__nome__icontains=query) &
        Q(quantidade__lte=F('id_produto__estoque_minimo'))
    ).order_by('id_produto__nome', 'numero_lote')

    return render(request, 'critical_stock_report.html', {
        'lotes': lotes,
        'query': query
    })

@login_required
def abc_curve_report(request):
    query = request.GET.get('q', '')

    filtros = Q()
    if query:
        filtros &= Q(id_lote__id_produto__nome__icontains=query)

    movimentações = MovimentaçãoEstoque.objects.filter(filtros).values('id_lote__id_produto').annotate(
        total_movimentado=Sum('quantidade')
    ).order_by('-total_movimentado')

    total_geral = sum(item['total_movimentado'] for item in movimentações) or 1
    produtos_abc = []
    acumulado = 0
    for item in movimentações:
        try:
            produto = Produto.objects.get(id_produto=item['id_lote__id_produto'])
            quantidade = item['total_movimentado']
            percentual = (quantidade / total_geral * 100)
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
        except Produto.DoesNotExist:
            continue

    return render(request, 'abc_curve_report.html', {
        'produtos_abc': produtos_abc,
        'query': query
    })

@login_required
def validity_report(request):
    query = request.GET.get('q', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    # Depuração: Exibir parâmetros recebidos
    print(f"Parâmetros recebidos: query='{query}', data_inicio='{data_inicio}', data_fim='{data_fim}'")

    # Filtrar lotes por nome do produto e data de validade
    filtros = Q(id_produto__nome__icontains=query)
    if data_inicio:
        filtros &= Q(data_validade__gte=data_inicio)
    if data_fim:
        filtros &= Q(data_validade__lte=data_fim)

    # Obter lotes com quantidade positiva
    lotes = Lote.objects.select_related('id_produto').filter(filtros, quantidade__gt=0).order_by('id_produto__nome', 'data_validade')

    # Depuração: Exibir lotes retornados
    print(f"Lotes retornados: {list(lotes.values('id_produto__nome', 'numero_lote', 'data_validade', 'quantidade'))}")

    # Adicionar status de validade
    today = date.today()
    validity_threshold = today + timedelta(days=30)  # Lotes próximos de vencer (30 dias)
    for lote in lotes:
        if lote.data_validade < today:
            lote.validity_status = 'Vencido'
            lote.validity_class = 'table-danger'
        elif lote.data_validade <= validity_threshold:
            lote.validity_status = 'Próximo do Vencimento'
            lote.validity_class = 'table-warning'
        else:
            lote.validity_status = 'Válido'
            lote.validity_class = 'table-success'

    return render(request, 'validity_report.html', {
        'lotes': lotes,
        'query': query,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })

@login_required
def send_critical_stock_alert():
    lotes = Lote.objects.select_related('id_produto').filter(
        quantidade__lte=F('id_produto__estoque_minimo')
    )
    for lote in lotes:
        print(f"Alerta: Estoque crítico para {lote.id_produto.nome} (Lote: {lote.numero_lote}) - Estoque atual: {lote.quantidade}")