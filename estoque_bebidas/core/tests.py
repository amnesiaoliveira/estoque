from django.test import TestCase
from .models import Produto, Fornecedor, MovimentaçãoEstoque, Usuário, Lote
from django.urls import reverse

class EstoqueTestCase(TestCase):
    def setUp(self):
        self.fornecedor = Fornecedor.objects.create(nome="Fornecedor Teste", contato="123456789", endereco="Rua Teste")
        self.produto = Produto.objects.create(
            nome="Cerveja", descricao="Cerveja artesanal", categoria="Alcoolica",
            preco=10.00, estoque_minimo=10, id_fornecedor=self.fornecedor, volumetria="Lata"
        )
        self.lote = Lote.objects.create(id_produto=self.produto, numero_lote="L123", data_validade="2025-12-31", quantidade=100)
        self.usuario = Usuário.objects.create_user(username="teste", password="teste123", papel="Gerente")

    def test_cadastro_produto_sem_lote(self):
        self.assertEqual(self.produto.nome, "Cerveja")
        self.assertEqual(self.produto.volumetria, "Lata")
        self.assertEqual(self.produto.estoque_atual, 0)

    def test_movimentacao_entrada(self):
        self.client.login(username="teste", password="teste123")
        response = self.client.post(reverse('movimentação_estoque_create'), {
            'id_lote': self.lote.id_lote,
            'tipo_movimentacao': 'Entrada',
            'quantidade': 50,
            'motivo': 'Compra',
            'numero_lote': 'L123',
            'data_validade': '2025-12-31'
        })
        self.lote.refresh_from_db()
        self.produto.refresh_from_db()
        self.assertEqual(self.lote.quantidade, 150)
        self.assertEqual(self.produto.estoque_atual, 150)
        self.assertRedirects(response, reverse('movimentação_estoque_list'))

    def test_movimentacao_saida(self):
        self.client.login(username="teste", password="teste123")
        response = self.client.post(reverse('movimentação_estoque_create'), {
            'id_lote': self.lote.id_lote,
            'tipo_movimentacao': 'Saida',
            'quantidade': 30,
            'motivo': 'Venda'
        })
        self.lote.refresh_from_db()
        self.produto.refresh_from_db()
        self.assertEqual(self.lote.quantidade, 70)
        self.assertEqual(self.produto.estoque_atual, 70)
        self.assertRedirects(response, reverse('movimentação_estoque_list'))