from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import HttpResponse
from django.utils import timezone
from .utilidades import verify_password
from django.http import JsonResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from .forms import ProductoForm, HorarioForm, FiltroHorarioForm, PasswordResetForm
from django.db.models import F, Sum
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes


def primera(request):
    estado = request.session.get("path", None)
    if estado:
        return redirect('index')
    else:
        return render(request, 'primera.html')

def index(request):

    verificar = request.session.get("path", False)
    
    if verificar:
        productos = Producto.objects.all()
        categorias = Categoria.objects.all()  # Obtener todas las categorías
        return render(request, 'index.html', {'productos': productos, 'categorias': categorias})
    else:
        return redirect('primera')
    

def vista_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria_id, estado=1)
    return render(request, 'categoria_detalle.html', {'categoria': categoria, 'productos': productos})


def login(request):
    verificar = request.session.get("path", False)
    if verificar:
        return redirect("index")
    else:
        if request.method == "POST":
            correo = request.POST.get("correo")
            clave = request.POST.get("clave")
            try:
                q = Usuario.objects.get(correo=correo, clave=clave)
                # print(q)
                #if verify_password(clave, q.clave):
                request.session["path"] = {
                    "id": q.id,
                    "nombre": q.nombre,
                    "apellido": q.apellidos,
                    "correo": q.correo,
                    "telefono": q.telefono,
                    "rol": q.rol,
                }
                return redirect("index")
                # else:
                #     raise Usuario.DoesNotExist()
                
            except Usuario.DoesNotExist:
                print("Usuario o contraseña incorrectos")
                messages.warning(request, "Usuario o contraseña incorrectos")
                request.session["path"] = None
            except Exception as e:
                print(f"Error: {e}")
                messages.error(request, f"Error: {e}")
                request.session["path"] = None
            return redirect("login")
        else:
            verificar = request.session.get("path", False)
            if verificar:
                return redirect("index")
            else:
                return render(request, "login.html")

def logout(request):
    verificar = request.session.get("path", False)
    if verificar:
        del request.session["path"]
        return redirect("primera")
    else:
        return redirect("login")

def password_reset_request(request):
    if request.method == "POST":
        print("Formulario enviado")
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            print(f"Correo recibido: {email}")
            try:
                user = Usuario.objects.get(correo=email)
                print(f"Usuario encontrado: {user}")
                print(f"ID del usuario: {user.id}")
                
                # Generar token y URL
                try:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.id))
                    reset_url = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")
                    print(f"URL de restablecimiento: {reset_url}")
                    
                    # Enviar correo
                    subject = "Recuperación de contraseña"
                    message = render_to_string('password_reset_email.html', {'reset_url': reset_url})
                    send_mail(subject, message, 'nicolvale1807@gmail.com', [email])
                    
                    messages.success(request, "Se ha enviado un enlace de recuperación a tu correo.")
                    return redirect('login')
                except Exception as e:
                    print(f"Error al generar el enlace de recuperación: {e}")
                    messages.error(request, "Ocurrió un error al generar el enlace de recuperación.")
            except Usuario.DoesNotExist:
                print("Usuario no encontrado")
                messages.error(request, "No se encontró un usuario con ese correo.")
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_form.html', {'form': form})

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Usuario.objects.get(id=uid)
    except (Usuario.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.clave = new_password
                user.save()
                messages.success(request, "Tu contraseña ha sido restablecida.")
                return redirect('login')
            else:
                messages.error(request, "Las contraseñas no coinciden.")
        return render(request, 'reset_password_form.html')
    else:
        messages.error(request, "El enlace de recuperación no es válido o ha expirado.")
        return redirect('password_reset_request')

def crear_cuenta_cliente(request):
    if request.method == "POST":
        nombre = request.POST.get('nombreCliente').lower()
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        total_fiado = request.POST.get('totalFiado')
        cliente = get_object_or_404(Cliente, nombre=nombre).lower()
        if cliente:
            # Si existe, actualizar el restante
            cliente.restante += Decimal(total_fiado)
            cliente.deben += Decimal(total_fiado)  # Opcional: actualizar el total de deuda
            cliente.save()
            messages.success(request, f"El cliente '{nombre}' ya existe. Se actualizó su restante.")
            return redirect('lista_fiados')
        else:

            # Crear el cliente
            cliente = Cliente.objects.create(
                nombre=nombre,
                apellidos=apellidos,
                telefono=telefono,
                deben=Decimal(total_fiado),  # Asegúrate de convertir a Decimal
                abonos=Decimal('0.00'),  # Inicializar abonos a 0
                restante=Decimal(total_fiado)  # Inicializar restante al total fiado
            )

            # Crear la deuda asociada al cliente
            Deuda.objects.create(
                cliente=cliente,
                abonos=Decimal('0.00'),  # Inicializar abonos a 0
                restante=Decimal(total_fiado)  # Inicializar restante al total fiado
            )

            return redirect('lista_fiados')  

    return render(request, 'crear_cuenta.html')



def lista_fiados(request):
    nombre_filtro = request.GET.get('nombre', '')

    deudas = Deuda.objects.select_related('cliente').all()

    # Si se quiere filtrar por nombre de cliente:
    if nombre_filtro:
        deudas = deudas.filter(cliente__nombre__icontains=nombre_filtro)

    datos_clientes = []
    for deuda in deudas:
        # Actualizar restante para reflejar deuda actual (opcional)
        deuda.restante = deuda.cliente.deben - deuda.abonos
        if deuda.restante < 0:
            deuda.restante = 0
        # Esto puede guardar el cambio para mantener sincronía con la DB, opcional:
        deuda.save(update_fields=['restante'])

        datos_clientes.append({
            'cliente': deuda.cliente,
            'deuda_total': deuda.cliente.deben,
            'abonos': deuda.abonos,
            'restante': deuda.restante,
            'deuda_id': deuda.id,
        })

    return render(request, 'fiados1.html', {'datos_clientes': datos_clientes})



def eliminar_cliente(request, cliente_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        return redirect('lista_fiados')
    except Exception as e:
        messages.error(request, "No se puede eliminar el cliente porque tiene deudas asociadas.")
        return redirect('lista_fiados')


def registrar_abono(request, deuda_id):
    rol_usuario = request.session.get('path', None)
    if rol_usuario is None or rol_usuario['rol'] not in [1, 2]:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('lista_fiados')
    deuda = get_object_or_404(Deuda, id=deuda_id)
    cliente = deuda.cliente
    if request.method == 'POST':
        abono_str = request.POST.get('abono')
        try:
            abono = Decimal(abono_str)
            if abono <= 0:
                error = "El abono debe ser un valor positivo."
                return render(request, 'abonar_deuda.html', {'deuda': deuda, 'error': error})
            if abono > deuda.restante:
                error = "El abono no puede ser mayor que la deuda restante."
                return render(request, 'abonar_deuda.html', {'deuda': deuda, 'error': error})
        except:
            error = "Ingrese un monto válido."
            return render(request, 'abonar_deuda.html', {'deuda': deuda, 'error': error})
        deuda.abonos += abono
        deuda.restante = cliente.deben - deuda.abonos
        if deuda.restante < 0:
            deuda.restante = Decimal('0.00')
        deuda.save()
        abonos_totales = Deuda.objects.filter(cliente=cliente).aggregate(total_abonos=Sum('abonos'))['total_abonos'] or Decimal('0.00')
        cliente.abonos = abonos_totales
        cliente.restante = cliente.deben - cliente.abonos
        if cliente.restante < 0:
            cliente.restante = Decimal('0.00')
        cliente.save()
        messages.success(request, 'Abono registrado correctamente.')
        return redirect('lista_fiados')
    return render(request, 'abonar_deuda.html', {'deuda': deuda})

def nuevo_producto(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto registrado correctamente.')
            return redirect('nuevo_producto')  # o a donde quieras redirigir
    else:
        form = ProductoForm()
    
    productos = Producto.objects.all()
    return render(request, 'nuevo_producto.html', {'form': form, 'productos': productos})



def registro_horarios(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    horarios = Horario.objects.all().order_by('-fecha')
    
    usuarios = Usuario.objects.filter(rol=1)  

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        horas_inicio = request.POST.get('horas_inicio')
        horas_fin = request.POST.get('horas_fin')
        usuario_id = request.POST.get('usuario')

        usuario = get_object_or_404(Usuario, id=usuario_id)
        nuevo_horario = Horario(
            fecha=fecha,
            horas_inicio=horas_inicio,
            horas_fin=horas_fin,
            usuario=usuario
        )
        nuevo_horario.save()
        messages.success(request, "Registro de horario agregado exitosamente.")
        return redirect('registro_horarios')

    return render(request, 'horarios.html', {
        'horarios': horarios,
        'usuarios': usuarios,
    })


def eliminar_horario(request, horario_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    try:
        horario = get_object_or_404(Horario, id=horario_id)
        horario.delete()
        return redirect('registro_horarios')
    except Exception as e:
        messages.error(request, "No se puede eliminar el horario porque tiene registros asociados.")
        return redirect('registro_horarios')

def agregar_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))

        producto = Producto.objects.get(id=producto_id)

        # Aquí puedes usar sesión o un modelo temporal (ej: Carrito por usuario)
        carrito = request.session.get('carrito', [])
        carrito.append({'id': producto.id, 'nombre': producto.nombre, 'cantidad': cantidad, 'precio': float(producto.precio)})
        request.session['carrito'] = carrito
        messages.success(request, f"Producto '{producto.nombre}' añadido correctamente al carrito.")

        return redirect('ver_carrito')
    return redirect('ver_carrito')



def vista_carrito(request):
    carrito = request.session.get('carrito', {})
    for producto_id, item in carrito.items():
        item['subtotal'] = item ['precio'] * item['cantidad']
    total_general = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    
    return render(request, 'carrito.html', {'carrito': carrito, 'total_general': total_general})

def agregar_producto_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        producto = Producto.objects.get(id=producto_id)

        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser al menos 1.")
            return redirect('carrito')
        carrito = request.session.get('carrito', {})

        if cantidad > producto.stock:
            messages.error(request, f"No hay suficiente stock para '{producto.nombre}'. Stock disponible: {producto.stock}.")
            return redirect('carrito')
        if producto_id in carrito:
            carrito[producto_id]['cantidad'] += cantidad
            if carrito[producto_id]['cantidad'] > producto.stock:
                messages.error(request, f"No hay suficiente stock para '{producto.nombre}'. Stock disponible: {producto.stock}.")
                carrito[producto_id]['cantidad'] = producto.stock
                return redirect('carrito')
        else:
            carrito[producto_id] = {
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio': float(producto.precio)
            }

        request.session['carrito'] = carrito
        messages.success(request, f"Producto '{producto.nombre}' añadido al carrito.")

        return redirect('carrito')

def eliminar_producto_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')

        carrito = request.session.get('carrito', {})

        if producto_id in carrito:
            del carrito[producto_id]
            messages.success(request, f"Producto eliminado del carrito.")

        request.session['carrito'] = carrito
        return redirect('carrito')

def finalizar_compra(request):
    if request.method == 'POST':
        mesa = int(request.POST.get('mesa'))
        carrito_session = request.session.get('carrito', {})
        
        if not carrito_session:
            messages.error(request, "El carrito está vacío.")
            return redirect('carrito')

        # Crear un carrito en la base de datos
        total_carrito = sum(item['precio'] * item['cantidad'] for item in carrito_session.values())
        carrito_db = Carrito.objects.create(
            total=total_carrito,
            estado=1
        )

        # Guardar cada detalle
        for producto_id, item in carrito_session.items():
            producto = Producto.objects.get(id=producto_id)
            DetalleCarrito.objects.create(
                producto=producto,
                carrito=carrito_db,
                cantidad=item['cantidad'],
                precio=item['precio'],
                mesa=mesa
            )

            # Opcional: actualizar stock
            producto.stock -= item['cantidad']
            producto.save()

        # Vaciar carrito de la sesión
        request.session['carrito'] = {}

        messages.success(request, f"Compra finalizada para la mesa {mesa}.")
        return redirect('index')

    return redirect('carrito')

def descargar_pdf_detalle_carrito(request):
    detalles = DetalleCarrito.objects.all()
    html = render_to_string('descargar_pdf_detalle_carrito.html', {'detalles': detalles})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="descargar_detalle_carrito.pdf"'

    pisa_status = pisa.CreatePDF(src=html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

def vista_factura(request):
    logueado = request.session.get("path")
    if not logueado:
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect("login")
    if request.method == 'POST':
        mesa = request.POST.get('mesa')
        detalles = DetalleCarrito.objects.filter(mesa=mesa)
        if not detalles.exists():
            messages.error(request, "No se encontraron detalles para la mesa especificada.")
            return redirect("index")
        return render(request, 'facturas.html', {'detalles': detalles})
    else:
        return render(request, 'facturas.html.html')
    

def crear_producto(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    registrado = False  # Variable para saber si ya se registró
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            registrado = True
            # No redireccionamos, dejamos que el mensaje se vea antes de que el JavaScript cierre
    else:
        form = ProductoForm()
    return render(request, 'formulario.html', {'form': form, 'registrado': registrado})



def nuevo_producto(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        foto = request.FILES.get('foto')
        categorias = request.POST.get('categoria')
        categoria = Categoria.objects.get(nombre=categorias)  # Obtener la categoría seleccionada
        # valor como '1', '2', etc.

        # Crear el producto con la categoría seleccionada (como texto)
        productos = Producto.objects.create(
            nombre=nombre,
            precio=precio,
            stock=stock,
            foto=foto,
            categoria=categoria
        )

        messages.success(request, 'Producto registrado correctamente.')
        return redirect('nuevo_producto')
    else:
        productos = Producto.objects.all()
        categorias = Categoria.objects.all()  # lista de opciones [('1', 'Cervezas'), ...]

    return render(request, 'nuevo_producto.html', {
        'productos': productos,
        'categorias': categorias
    })



def eliminar_producto(request, producto_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('nuevo_producto')
    except Exception as e:
        messages.error(request, "No se puede eliminar el producto porque tiene ventas asociadas.")
        return redirect('nuevo_producto')

def editar_producto(request, producto_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('nuevo_producto')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'form': form})


def lista_categorias(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    lista_categorias = request.GET.get('lista_categorias', '')
    if lista_categorias:
        categorias = Categoria.objects.filter(nombre__icontains=lista_categorias)
    else:
        categorias = Categoria.objects.all()
    return render(request, 'listar_categoria.html', {'categorias': categorias, 'lista_categorias': lista_categorias})

def crear_categoria(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        foto = request.FILES.get('foto')

        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect('crear_categoria')

        categoria = Categoria(nombre=nombre, foto=foto)
        try:
            categoria.save()
            messages.success(request, f"Categoría '{nombre}' creada con éxito.")
            return redirect('listar_categoria')
        except Exception as e:
            messages.error(request, f"Error al crear la categoría: {str(e)}")
            return redirect('crear_categoria')

    return render(request, 'crear_categoria.html')

def editar_categoria(request, categoria_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        foto = request.FILES.get('foto')

        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect('editar_categoria', categoria_id=categoria.id)

        categoria.nombre = nombre
        if foto:
            categoria.foto = foto
        try:
            categoria.save()
            messages.success(request, f"Categoría '{nombre}' actualizada con éxito.")
            return redirect('listar_categoria')
        except Exception as e:
            messages.error(request, f"Error al actualizar la categoría: {str(e)}")
            return redirect('editar_categoria', categoria_id=categoria.id)

    return render(request, 'editar_categoria.html', {'categoria': categoria})

def eliminar_categoria(request, categoria_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, f"Categoría '{categoria.nombre}' eliminada con éxito.")
            return redirect('listar_categoria')
        except Exception as e:
            messages.error(request, "No se puede eliminar la categoría porque tiene productos asociados.")
            return redirect('listar_categoria')
    return render(request, 'eliminar_categoria.html', {'categoria': categoria})



def registro_ventas(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    """
    Vista para registrar las ventas agrupadas por tipo de producto (categoría).
    """
    # Obtener todas las categorías activas
    categorias = Categoria.objects.filter(estado=1)

    data = []
    for categoria in categorias:
        # Filtrar productos por categoría
        productos = Producto.objects.filter(categoria=categoria, estado=1)
        categoria_data = {
            'categoria_nombre': categoria.nombre,
            'productos': []
        }

        for producto in productos:
            # Calcular las ventas totales por producto
            ventas = DetalleCarrito.objects.filter(producto=producto).aggregate(total_ventas=Sum('cantidad'))
            total_ventas = ventas['total_ventas'] or 0  # Si no hay ventas, usar 0
            precio_unitario = producto.precio
            margen_ganancia = precio_unitario * total_ventas

            # Agregar los datos del producto a la categoría
            categoria_data['productos'].append({
                'producto': producto,
                'stock': producto.stock,
                'total_ventas': total_ventas,
                'precio_unitario': precio_unitario,
                'margen_ganancia': margen_ganancia,
            })

        # Agregar los datos de la categoría al conjunto de datos
        data.append(categoria_data)

    # Renderizar la plantilla con los datos procesados
    return render(request, 'registro_ventas.html', {'data': data})



def crear_usuario(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    nombre = request.POST.get('nombre')
    apellidos = request.POST.get('apellidos')
    telefono = request.POST.get('telefono')
    correo = request.POST.get('correo')
    clave = request.POST.get('clave')
    documento = request.POST.get('documento')
    rol = request.POST.get('rol')
    salario = request.POST.get('salario')
    
    try:
        if request.method == "POST":

            # Crear el nuevo usuario
            Usuario.objects.create(
                nombre=nombre,
                apellidos=apellidos,
                telefono=telefono,
                correo=correo,
                clave=clave,
                documento=documento,
                rol=rol,
                salario=Decimal(salario)
            )
            messages.success(request, "Usuario creado exitosamente.")
            return redirect('listar_usuarios')
    except Exception as e:
        messages.error(request, f"Error al crear el usuario")
        return redirect('crear_usuario')

    return render(request, 'crear_usuario.html')


def listar_usuarios(request):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    usuarios = Usuario.objects.all()
    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})


def editar_usuario(request, usuario_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == "POST":
        usuario.nombre = request.POST.get('nombre')
        usuario.apellidos = request.POST.get('apellidos')
        usuario.telefono = request.POST.get('telefono')
        usuario.correo = request.POST.get('correo')
        usuario.clave = request.POST.get('clave')
        usuario.documento = request.POST.get('documento')
        usuario.rol = request.POST.get('rol')
        usuario.salario = Decimal(request.POST.get('salario'))
        usuario.save()
        messages.success(request, "Usuario actualizado exitosamente.")
        return redirect('listar_usuarios')

    return render(request, 'editar_usuario.html', {'usuario': usuario})


def eliminar_usuario(request, usuario_id):
    # Verificar si el usuario tiene el rol de administrador
    usuario = request.session.get('path', None)
    if not usuario or usuario.get('rol') != 2:  # Suponiendo que 'rol=1' es el administrador
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('index')  # Redirigir a una página adecuada
    
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.delete()
        messages.success(request, "Usuario eliminado exitosamente.")
        return redirect('listar_usuarios')
    except Exception as e:
        messages.error(request, "No se puede eliminar el usuario porque tiene horarios asociados.")
        return redirect('listar_usuarios')


