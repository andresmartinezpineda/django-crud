# Importación de atajos y funciones útiles de Django
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm #Formularios prediseñados para autenticación
from django.contrib.auth.models import User # Modelo de usuario integrado de Django
from django.contrib.auth import login,logout,authenticate # Funciones de autenticación
from .forms import CreateTasks # Formulario personalizado para creación/edición de tareas
from .models import Task # Modelo de datos Task
from django.utils import timezone # Utilidad para manejo de fechas y horas
from django.contrib.auth.decorators import login_required # Decorador para proteger vistas que requieren autenticación

# Vista principal, muestra la página de inicio
def home(request):
    return render(request,'home.html')


# Vista de registro de usuarios
def signup(request):
    if request.method == 'GET':
        # Renderiza el formulario de creación de usuario en una petición GET
        form = UserCreationForm()
        return render(request,'signup.html',{
            'form': form
        })
    else:
        # Validación de contraseñas y creación de usuario en una petición POST
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user) # Autentica automáticamente al usuario
                return redirect('tasks')
            except:
                # Si el usuario ya existe o hay otro error
                form = UserCreationForm()
                return render(request,'signup.html',{
                    'form': form,
                    'error': 'username already exist'
                })
        else:
            # Contraseñas no coinciden
            form = UserCreationForm()
            return render(request,'signup.html',{
                'form': form,
                'error': 'passwords do not match'
            })


# Vista protegida: Lista de tareas pendientes del usuario autenticado
@login_required        
def tasks(request):
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'tasks.html',{
        'tasks': tasks
    })

# Vista protegida: Lista de tareas completadas, ordenadas por fecha de finalización
@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'tasks.html',{
        'tasks': tasks
    })

# Vista protegida: Detalle y edición de una tarea específica
@login_required
def task_detail(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user) # Garantiza que solo acceda a sus propias tareas
    
    if request.method == 'GET':
        # Renderiza el formulario precargado con los datos de la tarea
        form = CreateTasks(instance=task)
        return render(request,'task_detail.html',{
            'task': task,
            'form': form
        })
    else:
        try:
            # Actualiza los datos de la tarea con los datos del formulario
            form = CreateTasks(request.POST,instance=task)
            form.save()
            return redirect('tasks')
        except:
            # Manejo de errores durante la actualización
            return render(request,'task_detail.html',{
                'task': task,
                'form': form,
                'error': 'error updating task'
            })

# Vista protegida: Marcar una tarea como completada
@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now() # Establece la fecha de finalización
        task.save()
        return redirect('tasks')

# Vista protegida: Eliminar una tarea
@login_required
def delete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

# Vista protegida: Crear una nueva tarea
@login_required
def create_task(request):
    if request.method == 'GET':
        # Renderiza el formulario vacío para crear una nueva tarea
        return render(request,'create_task.html',{
            'form': CreateTasks()
        })
    else:
        try:
            form = CreateTasks(request.POST)
            new_task = form.save(commit=False) # No guarda aún en base de datos
            new_task.user = request.user # Asigna el usuario autenticado a la tarea
            new_task.save()
            return redirect('tasks')
        except ValueError:
            # Error en la validación de los datos del formulario
            return render(request,'create_task.html',{
                'form': CreateTasks(),
                'error': 'Please provide valid data'
            })

# Cierre de sesión del usuario autenticado
@login_required
def signout(request):
    logout(request)
    return redirect('home')

# Vista de inicio de sesión
def signin(request):
    if request.method == 'GET':
        return render(request,'signin.html',{
            'form': AuthenticationForm()
        })
    else:
        # Autenticación del usuario usando los datos del formulario
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])

        if not user is None:
            login(request,user)
            return redirect('tasks')
        else:
            # Credenciales inválidas
            return render(request,'signin.html',{
                'form': AuthenticationForm(),
                'error': 'Username or password is incorrect'
            })