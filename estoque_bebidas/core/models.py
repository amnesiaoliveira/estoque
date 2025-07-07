# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# Usuário
class Usuário(AbstractUser):
    ROLE_CHOICES = (
        ('Proprietario', 'Proprietário'),
        ('Gerente', 'Gerente'),
        ('Atendente', 'Atendente'),
    )
    papel = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Atendente')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuário'

    def __str__(self):
        return self.username

# Fornecedor
class Fornecedor(models.Model):
    id_fornecedor = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    contato = models.CharField(max_length=100)
    endereco = models.TextField()

    class Meta:
        db_table = 'fornecedor'

    def __str__(self):
        return self.nome

# Produto
class Produto(models.Model):
    CATEGORY_CHOICES = (
        ('Alcoolica', 'Alcoólica'),
        ('Nao_Alcoolica', 'Não Alcoólica'),
    )
    VOLUMETRIA_CHOICES = (
        ('Caixa', 'Caixa'),
        ('Garrafa', 'Garrafa'),
        ('Lata', 'Lata'),
        ('Barril', 'Barril'),
        ('Outros', 'Outros'),
    )
    id_produto = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque_minimo = models.IntegerField()
    estoque_atual = models.IntegerField(default=0)
    id_fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    volumetria = models.CharField(max_length=20, choices=VOLUMETRIA_CHOICES, default='Garrafa')

    class Meta:
        db_table = 'produto'

    def __str__(self):
        return f"{self.nome} ({self.get_volumetria_display()})"

# Lote
class Lote(models.Model):
    id_lote = models.AutoField(primary_key=True)
    id_produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=50)
    data_validade = models.DateField()
    quantidade = models.IntegerField(default=0)
    data_entrada = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lote'
        unique_together = [['id_produto', 'numero_lote']]

    def __str__(self):
        return f"Lote {self.numero_lote} - {self.id_produto.nome}"

# Movimentação de Estoque
class MovimentaçãoEstoque(models.Model):
    MOVEMENT_TYPE_CHOICES = (
        ('Entrada', 'Entrada'),
        ('Saida', 'Saída'),
        ('Ajuste', 'Ajuste'),
    )
    id_movimentacao = models.AutoField(primary_key=True)
    id_lote = models.ForeignKey(Lote, on_delete=models.CASCADE, null=True)  # Temporariamente nullable
    id_usuário = models.ForeignKey(Usuário, on_delete=models.CASCADE)
    tipo_movimentacao = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantidade = models.IntegerField()
    motivo = models.TextField()
    data_movimentacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'movimentação_estoque'

    def __str__(self):
        return f"{self.tipo_movimentacao} - {self.id_lote.id_produto.nome if self.id_lote else 'Sem Lote'} (Lote: {self.id_lote.numero_lote if self.id_lote else 'N/A'})"