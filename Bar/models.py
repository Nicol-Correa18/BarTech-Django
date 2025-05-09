from django.db import models
from datetime import timedelta
from django.core.validators import MinValueValidator, RegexValidator, EmailValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

solo_letras_numeros = RegexValidator(
    regex=r'^[a-zA-Z0-9 ]+$',
    message="No se permiten caracteres especiales. Solo letras, números y espacios."
)

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(validators=[MinValueValidator(0)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    STATUS = (
        (1, "Activo"),
        (2, "Inactivo")
    )
    estado = models.IntegerField(choices=STATUS, default=1)
    
    categoria = models.ForeignKey('Categoria', on_delete=models.DO_NOTHING, related_name="productos")
    foto = models.ImageField(upload_to="productos/")

    def clean(self):
        # Validación para asegurar que el stock y el precio sean mayores que 0
        if self.stock < 1:
            raise ValidationError("El stock debe ser mayor que 0.")
        if self.precio < 0:
            raise ValidationError("El precio no puede ser negativo.")

    def __str__(self):
        return f'{self.nombre}'

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, validators=[solo_letras_numeros])
    apellidos = models.CharField(max_length=100, validators=[solo_letras_numeros])
    telefono = models.CharField(max_length=15, validators=[solo_letras_numeros])
    deben = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    abonos = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    restante = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def clean(self):
        # Validación para asegurar que el teléfono tenga un formato válido (opcional)
        if len(self.telefono) < 10:
            raise ValidationError("El número de teléfono debe tener al menos 10 dígitos.")
        if self.deben < 0 or self.abonos < 0 or self.restante < 0:
            raise ValidationError("Los valores de deuda, abono o restante no pueden ser negativos.")

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'
    
class Deuda(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.DO_NOTHING, related_name="fk_cliente_deuda")
    abonos = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    restante = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.cliente.nombre} {self.abonos} {self.restante}'
    
class Carrito(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    ESTADOS = (
        (1, "Pendiente"),
        (2, "Pagado")
    )
    estado = models.IntegerField(choices=ESTADOS, default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name="fk_cliente_carrito", null=True)

    def clean(self):
        if self.total < Decimal('0.00'):
            raise ValidationError("El total del carrito no puede ser negativo.")

    def __str__(self):
        return f'{self.id}'
        # return f"Carrito de {self.cliente.nombre} - Estado: {self.estado}"


class DetalleCarrito(models.Model):
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])  # La cantidad no puede ser menor que 1
    mesa = models.IntegerField(validators=[MinValueValidator(1)])  # La mesa debe ser un número positivo
    producto = models.ForeignKey('Producto', on_delete=models.DO_NOTHING)
    carrito = models.ForeignKey('Carrito', on_delete=models.DO_NOTHING, null=True)

    def clean(self):
        if self.precio < Decimal('0.00'):
            raise ValidationError("El precio no puede ser negativo.")
        if self.cantidad < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")
        if self.mesa < 1:
            raise ValidationError("El número de mesa debe ser un valor positivo.")

    # def _str_(self):
    #     return f"Detalle del carrito {self.carrito.id} - Producto: {self.producto.nombre}"

class Usuario(models.Model):
    nombre = models.CharField(max_length=100, validators=[RegexValidator(regex=r'^[a-zA-Z ]+$', message="Solo se permiten letras y espacios.")])
    apellidos = models.CharField(max_length=100, validators=[RegexValidator(regex=r'^[a-zA-Z ]+$', message="Solo se permiten letras y espacios.")])
    telefono = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message="El número de teléfono debe ser válido.")])
    correo = models.EmailField(unique=True, validators=[EmailValidator(message="Correo electrónico inválido.")])
    clave = models.CharField(max_length=20, validators=[RegexValidator(regex=r'^[a-zA-Z0-9@#$%^&+=]*$', message="La clave solo puede contener letras, números y caracteres especiales.")])
    documento = models.CharField(max_length=20, unique=True, validators=[RegexValidator(regex=r'^\d{5,20}$', message="El documento debe ser un número válido.")])
    ROLES = (
        (1, 'EMPLEADOS'),
        (2, 'ADMINISTRADOR')
    )
    rol = models.IntegerField(choices=ROLES, default=1)
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    last_login = models.DateTimeField(default=now, blank=True, null=True)
    password = models.CharField(max_length=128, default=make_password(''), validators=[RegexValidator(regex=r'^[a-zA-Z0-9@#$%^&+=]*$', message="La clave solo puede contener letras, números y caracteres especiales.")])
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    
    def clean(self):    
        if self.salario < Decimal('0.00'):
            raise ValidationError("El salario no puede ser negativo.")
    
    def __str__(self):
        return f"{self.rol} - {self.nombre}"
    
    def get_email_field_name(self):
        return 'correo'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

class Horario(models.Model):
    horas_inicio = models.TimeField()
    horas_fin = models.TimeField()
    fecha = models.DateField()
    usuario = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING)

    @property
    def horas_trabajadas(self):
        inicio = datetime.combine(self.fecha, self.horas_inicio)
        fin = datetime.combine(self.fecha, self.horas_fin)
        if fin < inicio:
            fin += timedelta(days=1)  # Si el fin es antes que el inicio, es al día siguiente
        total_horas = (fin - inicio).seconds / 3600
        return round(total_horas, 2)

    def clean(self):
        if self.horas_inicio >= self.horas_fin:
            raise ValidationError("La hora de inicio debe ser antes de la hora de fin.")

    def __str__(self):
        return f"Horario de {self.usuario.nombre} - Fecha: {self.fecha}"
    
class Categoria(models.Model):
    nombre= models.CharField(max_length=100)
    foto = models.ImageField(upload_to="categorias/")
    STATUS = (
        (1, "Activo"),
        (2, "Inactivo")
    )
    estado = models.IntegerField(choices=STATUS, default=1)

    def __str__(self):
        return f"{self.nombre}"


