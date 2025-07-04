# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    # Rotas de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Rotas da Aplicação
    path('', views.index, name='index'),
    path('editar/<int:pk>/', views.edit_transacao, name='edit_transacao'),
    path('excluir/<int:pk>/', views.delete_transacao, name='delete_transacao'),

    # NOVA ROTA para a página de relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
]