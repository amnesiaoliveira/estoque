import os
import django
from faker import Faker
import random
from datetime import date, timedelta

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estoque_bebidas.settings')
django.setup()

from core.models import Fornecedor, Produto

# Inicializar o Faker
fake = Faker('pt_BR')  # Localizado para português do Brasil

def populate_fornecedores(n=50):
    print("Criando fornecedores...")
    for _ in range(n):
        Fornecedor.objects.create(
            nome=fake.company(),
            contato=fake.phone_number(),
            endereco=fake.address()
        )
    print(f"{n} fornecedores criados com sucesso!")

def populate_produtos(n=500):
    print("Criando produtos...")
    fornecedores = list(Fornecedor.objects.all())  # Lista de fornecedores existentes
    if not fornecedores:
        print("Nenhum fornecedor encontrado. Crie fornecedores primeiro.")
        return

    categorias = ['Alcoolica', 'Nao_Alcoolica']
    bebidas_alcoolicas = [
        "Cerveja", "Vinho", "Whisky", "Vodka", "Tequila", "Cachaça", "Gin", "Rum", "Licor"
    ]
    bebidas_nao_alcoolicas = [
        "Refrigerante", "Suco", "Água", "Chá Gelado", "Energético", "Água de Coco"
    ]

    for _ in range(n):
        categoria = random.choice(categorias)
        if categoria == 'Alcoolica':
            nome_base = random.choice(bebidas_alcoolicas)
        else:
            nome_base = random.choice(bebidas_nao_alcoolicas)
        
        # Gerar nome com marca fictícia
        nome = f"{nome_base} {fake.word().capitalize()} {random.randint(100, 999)}"
        
        Produto.objects.create(
            nome=nome,
            descricao=fake.text(max_nb_chars=200),
            categoria=categoria,
            preco=round(random.uniform(5.0, 100.0), 2),
            data_validade=fake.date_between(start_date='today', end_date='+2y'),
            estoque_minimo=random.randint(10, 50),
            estoque_atual=random.randint(0, 100),
            id_fornecedor=random.choice(fornecedores)
        )
    print(f"{n} produtos criados com sucesso!")

if __name__ == '__main__':
    populate_fornecedores(50)
    populate_produtos(500)