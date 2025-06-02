from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Produto, Fornecedor, MovimentaçãoEstoque, Usuário

class UsuárioRegisterForm(UserCreationForm):
    email = forms.EmailField()
    papel = forms.ChoiceField(choices=Usuário.ROLE_CHOICES)

    class Meta:
        model = Usuário
        fields = ['username', 'email', 'password1', 'password2', 'papel']

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'contato', 'endereco']

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'categoria', 'preco', 'data_validade', 'estoque_minimo', 'id_fornecedor']
        widgets = {
            'data_validade': forms.DateInput(attrs={'type': 'date'}),
        }

class MovimentaçãoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentaçãoEstoque
        fields = ['id_produto', 'tipo_movimentacao', 'quantidade', 'motivo']