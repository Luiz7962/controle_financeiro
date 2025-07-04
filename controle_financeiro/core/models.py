from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Importe o timezone do Django

TIPO_CHOICES = (
    ('Receita', 'Receita'),
    ('Despesa', 'Despesa'),
)

class Transacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # CAMPO MODIFICADO: Removemos auto_now_add e adicionamos um valor padrão.
    # Agora o usuário pode escolher a data, que por padrão será o dia de hoje.
    data = models.DateTimeField(default=timezone.now)
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_display()})"
