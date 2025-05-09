from django.contrib import admin
from .models import *

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellidos', 'telefono']

@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'abonos', 'restante']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellidos', 'telefono', 'correo', 'clave', 'documento', 'rol']
    list_filter = ['rol']


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('horas_inicio', 'horas_fin', 'usuario', 'fecha')
    list_filter = ('usuario', 'fecha')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria', 'stock', 'foto']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'estado', 'total', 'cliente']

@admin.register(DetalleCarrito)
class DetalleCarritoAdmin(admin.ModelAdmin):
    list_display = ['precio', 'cantidad', 'mesa', 'producto', 'carrito']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'foto']

