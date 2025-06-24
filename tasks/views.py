from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from .forms import CreateTasks
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request,'home.html')

def signup(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render(request,'signup.html',{
            'form': form
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('tasks')
            except:
                form = UserCreationForm()
                return render(request,'signup.html',{
                    'form': form,
                    'error': 'username already exist'
                })
        else:
            form = UserCreationForm()
            return render(request,'signup.html',{
                'form': form,
                'error': 'passwords do not match'
            })

@login_required        
def tasks(request):
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'tasks.html',{
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'tasks.html',{
        'tasks': tasks
    })

@login_required
def task_detail(request,task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task,pk=task_id,user=request.user)
        form = CreateTasks(instance=task)
        return render(request,'task_detail.html',{
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task,pk=task_id,user=request.user)
            form = CreateTasks(request.POST,instance=task)
            form.save()
            return redirect('tasks')
        except:
            return render(request,'task_detail.html',{
                'task': task,
                'form': form,
                'error': 'error updating task'
            })
    
@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request,'create_task.html',{
            'form': CreateTasks()
        })
    else:
        try:
            form = CreateTasks(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save() 
            print(new_task)
            return redirect('tasks')
        except ValueError:
            return render(request,'create_task.html',{
                'form': CreateTasks(),
                'error': 'Please provide valid data'
            })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request,'signin.html',{
            'form': AuthenticationForm()
        })
    else:
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])

        if not user is None:
            login(request,user)
            return redirect('tasks')
        else:
            return render(request,'signin.html',{
                'form': AuthenticationForm(),
                'error': 'Username or password is incorrect'
            })