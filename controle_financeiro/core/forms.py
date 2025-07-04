from django import forms
from .models import Transacao

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        # Adicionamos 'data' à lista de campos.
        fields = ['data', 'descricao', 'valor', 'tipo', 'categoria']
        
        # Adicionamos um widget para o campo 'data'.
        widgets = {
            # Este widget renderiza um campo de data HTML5, que a maioria dos navegadores
            # transforma em um calendário para o usuário escolher a data.
            'data': forms.DateInput(
                attrs={
                    'type': 'date', # Isso é o mais importante!
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
                }
            ),
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Ex: Salário, Aluguel, Supermercado'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Ex: 150.75'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Ex: Moradia, Trabalho, Lazer'
            }),
        }
