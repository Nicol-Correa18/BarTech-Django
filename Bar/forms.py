from django import forms
from .models import Producto, Horario, Usuario, Cliente, Categoria

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock', 'categoria','estado',  'foto']
        widgets = {
            'categoria': forms.Select(),
            'estado': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()
        self.fields['estado'].choices = Producto.STATUS


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['fecha', 'usuario', 'horas_inicio', 'horas_fin']
        widgets = {
            'horas_inicio': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'horas_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

class FiltroHorarioForm(forms.Form):
    fecha = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    trabajador = forms.ModelChoiceField(queryset=Usuario.objects.all(), required=False)

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'deben'] 

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico", max_length=254)