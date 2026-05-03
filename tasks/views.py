from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import DatabaseError, IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TaskForm
from .models import Task


# Create your views here.
#Vista a la ruta de usuario
def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('tasks')

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm()
        })

    form = UserCreationForm(request.POST)

    try:
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
    except IntegrityError:
        return render(request, 'signup.html', {
            'form': form,
            'error': 'No se pudo crear el usuario. Intenta con otro nombre.',
        }, status=400)
    except DatabaseError:
        return render(request, 'signup.html', {
            'form': form,
            'error': 'La base de datos no está disponible. Revisa DATABASE_URL en Render.',
        }, status=503)

    return render(request, 'signup.html', {
        'form': form,
        'error': 'No se pudo crear el usuario. Revisa los datos.',
    }, status=400)


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)

    return render(request, 'tasks.html', {
        'tasks': tasks,
        'title': '📋 Tasks Pending'
    })


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(
        user=request.user,
        datecompleted__isnull=False,
    ).order_by('-datecompleted')
    return render(request, 'tasks.html', {
        'tasks': tasks,
        'title': 'Tasks Completed'
    })


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm()
        })

    form = TaskForm(request.POST)
    if form.is_valid():
        new_task = form.save(commit=False)
        new_task.user = request.user
        new_task.save()
        return redirect('tasks')

    return render(request, 'create_task.html', {
        'form': form,
        'error': 'Please provide valid data'
    }, status=400)
            
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if task.datecompleted:
        return render(request, 'task_detail.html', {
            'task': task,
            'form': None,
            'error': 'This task is already completed and cannot be edited'
        })

    if request.method == 'GET':
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })

    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
        form.save()
        return redirect('tasks')

    return render(request, 'task_detail.html', {
        'task': task,
        'form': form,
        'error': 'Error updating task. Please provide valid data.'
    }, status=400)

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
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.user.is_authenticated:
        return redirect('tasks')

    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm()
        })

    form = AuthenticationForm(request, data=request.POST)
    try:
        if form.is_valid():
            login(request, form.get_user())
            return redirect('tasks')
    except DatabaseError:
        return render(request, 'signin.html', {
            'form': form,
            'error': 'La base de datos no está disponible. Revisa DATABASE_URL en Render.'
        }, status=503)

    return render(request, 'signin.html', {
        'form': form,
        'error': 'Usuario o contraseña incorrecta'
    }, status=400)
