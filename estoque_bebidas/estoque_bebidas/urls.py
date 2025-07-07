from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('fornecedores/', views.fornecedor_list, name='fornecedor_list'),
    path('fornecedores/edit/<int:id_fornecedor>/', views.fornecedor_edit, name='fornecedor_edit'),
    path('fornecedores/create/', views.fornecedor_create, name='fornecedor_create'),
    path('produtos/', views.produto_list, name='produto_list'),
    path('produtos/edit/<int:id_produto>/', views.produto_edit, name='produto_edit'),
    path('produtos/create/', views.produto_create, name='produto_create'),
    path('movimentações/', views.movimentação_estoque_list, name='movimentação_estoque_list'),
    path('movimentações/create/', views.movimentação_estoque_create, name='movimentação_estoque_create'),
    path('relatorios/estoque/', views.stock_report, name='stock_report'),
    path('relatorios/critico/', views.critical_stock_report, name='critical_stock_report'),
    path('abc_curve_report/', views.abc_curve_report, name='abc_curve_report'),
    path('get_lotes/', views.get_lotes, name='get_lotes'),
    path('relatorios/validade/', views.validity_report, name='validity_report'),
]