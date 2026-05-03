from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
#Vista a la ruta de usuario
def home(request):
    return render(request, 'home.html')
#Vista
def signup(request):

    if request.method == 'GET': #entra por get(abre la pagina)
       return render(request, 'signup.html', {
            'form': UserCreationForm()
         })
    else:
        if request.POST['password1'] == request.POST['password2']: #Verifica que ambas contrasenas sean iguales
            try: #Si son iguales entra en try
                #register user. Creacion de usuario en la bd 
                user = User.objects.create_user(username=request.POST['username'], #metodo para crear un objeto nuevo
                password=request.POST['password1'])# Le pasamos el usuario y la contrasena
                user.save()# lo guardamos
                login(request, user) #INICIAMOS SESION
                return redirect('tasks') #redireccionamos a home
            except IntegrityError: #Si el usuario ya existe entra en except
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })
        return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Las contraseñas no coinciden'
        })
  
@login_required     
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    
    return render(request, 'tasks.html',{
        'tasks': tasks,
        'title': '📋 Tasks Pending'
    })
    

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by
    ('-datecompleted')
    return render(request, 'tasks.html',{
        'tasks': tasks,
        'title': 'Tasks Completed'
    })


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html',{
            'form': TaskForm()
        })
    else: 
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks') 
        except ValueError:
            return render(request, 'create_task.html',{
                'form': TaskForm,
                'error': 'Please provide valid data'
         })
            
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    
    #Si la tarea ya esta completada, no permitr edicion
    if task.datecompleted:
        return render(request, 'task_detail.html',{
        'task': task,
        'form': None,
        'error': 'This task is already completed and cannot be edited'
    })
    
    
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form =TaskForm(instance=task)
        return render(request, 'task_detail.html',{
        'task': task,
        'form': form
    })
    else:
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')
        else:
            return render(request, 'task_detail.html',{
                'task': task,
                'form': form,
                'error': 'Error updating task. Please provide valid data.'
            })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
   
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
   
@login_required
def signout(request):#Vista para cerrar sesion
      logout(request) #CERRAMOS SESION
      return redirect('home') #REDIRECCIONAMOS A HOME
    
def signin(request): #Vista para iniciar sesion
    if request.method == 'GET':
        return render(request, 'signin.html',{
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST
        ['password'])
        
        if user is None:
            return render(request, 'signin.html',{
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrecta'
            })
        else:
            login(request, user) #INICIAMOS SESION
            return redirect('tasks')
        
       