from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, F, Q
from .models import Produto, Fornecedor, MovimentaçãoEstoque, Usuário
from .forms import ProdutoForm, FornecedorForm, MovimentaçãoEstoqueForm, UsuárioRegisterForm

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
            form.save()
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
            Q(nome__icontains=query) | Q(categoria__icontains=query)
        )
    return render(request, 'produto_list.html', {'produtos': produtos, 'query': query})

# Movimentação de Estoque
@login_required
def movimentação_estoque_create(request):
    if request.method == 'POST':
        form = MovimentaçãoEstoqueForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.id_usuário = request.user
            produto = movement.id_produto
            if movement.tipo_movimentacao == 'Entrada':
                produto.estoque_atual += movement.quantidade
            elif movement.tipo_movimentacao == 'Saida':
                if produto.estoque_atual >= movement.quantidade:
                    produto.estoque_atual -= movement.quantidade
                else:
                    messages.error(request, 'Estoque insuficiente.')
                    return redirect('movimentação_estoque_create')
            elif movement.tipo_movimentacao == 'Ajuste':
                produto.estoque_atual = movement.quantidade
            produto.save()
            movement.save()
            messages.success(request, 'Movimentação registrada com sucesso!')
            return redirect('movimentação_estoque_list')
    else:
        form = MovimentaçãoEstoqueForm()
    return render(request, 'movimentação_estoque_form.html', {'form': form})

# Lista de Movimentações
@login_required
def movimentação_estoque_list(request):
    query = request.GET.get('q', '')
    movimentações = []
    if query:
        movimentações = MovimentaçãoEstoque.objects.filter(
            Q(id_produto__nome__icontains=query) |
            Q(tipo_movimentacao__icontains=query) |
            Q(motivo__icontains=query) |
            Q(id_usuário__username__icontains=query)
        )
    return render(request, 'movimentação_estoque_list.html', {'movimentações': movimentações, 'query': query})

# Relatório de Estoque Atual
@login_required
def stock_report(request):
    produtos = Produto.objects.all()
    return render(request, 'stock_report.html', {'produtos': produtos})

# Relatório de Produtos em Nível Crítico
@login_required
def critical_stock_report(request):
    produtos = Produto.objects.filter(estoque_atual__lte=F('estoque_minimo'))
    return render(request, 'critical_stock_report.html', {'produtos': produtos})