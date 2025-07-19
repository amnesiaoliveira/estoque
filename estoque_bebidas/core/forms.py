from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Produto, Fornecedor, MovimentaçãoEstoque, Usuário, Lote

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
        fields = ['nome', 'descricao', 'categoria', 'estoque_minimo', 'id_fornecedor', 'volumetria']

class MovimentaçãoEstoqueForm(forms.ModelForm):
    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), label="Produto")
    numero_lote = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Digite o número do lote'}))
    data_validade = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = MovimentaçãoEstoque
        fields = ['produto', 'id_lote', 'tipo_movimentacao', 'quantidade', 'motivo', 'numero_lote', 'data_validade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_lote'].queryset = Lote.objects.none()  # Inicialmente vazio
        self.fields['id_lote'].label = "Lote"
        self.fields['id_lote'].required = False
        if 'produto' in self.data:
            try:
                produto_id = int(self.data.get('produto'))
                self.fields['id_lote'].queryset = Lote.objects.filter(id_produto_id=produto_id)
            except (ValueError, TypeError):
                self.fields['id_lote'].queryset = Lote.objects.none()
        # Depuração
        print(f"Produto ID: {self.data.get('produto')}, Lotes disponíveis: {self.fields['id_lote'].queryset.count()}")

    def clean(self):
        cleaned_data = super().clean()
        tipo_movimentacao = cleaned_data.get('tipo_movimentacao')
        numero_lote = cleaned_data.get('numero_lote')
        data_validade = cleaned_data.get('data_validade')
        id_lote = cleaned_data.get('id_lote')
        produto = cleaned_data.get('produto')

        if not produto:
            raise forms.ValidationError('Selecione um produto.')

        if tipo_movimentacao == 'Entrada':
            if not numero_lote or not data_validade:
                raise forms.ValidationError('Número do lote e data de validade são obrigatórios para movimentações de entrada.')
        elif tipo_movimentacao in ['Saida', 'Ajuste']:
            if not id_lote:
                raise forms.ValidationError('Selecione um lote para saídas ou ajustes.')
            if id_lote and id_lote.id_produto != produto:
                raise forms.ValidationError('O lote selecionado não pertence ao produto escolhido.')

        return cleaned_data