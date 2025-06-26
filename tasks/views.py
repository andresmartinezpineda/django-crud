# Import useful Django shortcuts and authentication tools
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm # Built-in authentication forms
from django.contrib.auth.models import User # Django's default User model
from django.contrib.auth import login,logout,authenticate # Authentication functions
from .forms import CreateTasks # Custom form for creating/editing tasks
from .models import Task # Task data model
from django.utils import timezone # Utilities for date and time handling
from django.contrib.auth.decorators import login_required # Decorator to protect views for authenticated users only

# Public home page view
def home(request):
    return render(request,'home.html')


# User registration view
def signup(request):
    if request.method == 'GET':
        # Display the user creation form on GET requests
        form = UserCreationForm()
        return render(request,'signup.html',{
            'form': form
        })
    else:
        # Validate passwords and create a new user on POST requests
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user) # Automatically authenticate the user after registration
                return redirect('tasks')
            except:
                # Handle errors such as username already exists
                form = UserCreationForm()
                return render(request,'signup.html',{
                    'form': form,
                    'error': 'username already exist'
                })
        else:
            # Passwords do not match
            form = UserCreationForm()
            return render(request,'signup.html',{
                'form': form,
                'error': 'passwords do not match'
            })


# Protected view: Displays the list of pending tasks for the authenticated user
@login_required        
def tasks(request):
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'tasks.html',{
        'tasks': tasks
    })

# Protected view: Displays completed tasks, sorted by completion date
@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'tasks.html',{
        'tasks': tasks
    })

# Protected view: Displays task details and allows editing
@login_required
def task_detail(request,task_id):
    # Ensure the user can only access their own tasks
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    
    if request.method == 'GET':
        # Display the task form pre-filled with existing data
        form = CreateTasks(instance=task)
        return render(request,'task_detail.html',{
            'task': task,
            'form': form
        })
    else:
        try:
            # Update the task with the submitted form data
            form = CreateTasks(request.POST,instance=task)
            form.save()
            return redirect('tasks')
        except:
            # Handle form validation errors
            return render(request,'task_detail.html',{
                'task': task,
                'form': form,
                'error': 'error updating task'
            })

# Protected view: Mark a task as completed
@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now() # Set the completion date to the current time
        task.save()
        return redirect('tasks')

# Protected view: Delete a task
@login_required
def delete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


# Protected view: Create a new task
@login_required
def create_task(request):
    if request.method == 'GET':
        # Display an empty task creation form
        return render(request,'create_task.html',{
            'form': CreateTasks()
        })
    else:
        try:
            form = CreateTasks(request.POST)
            new_task = form.save(commit=False) # Do not save to the database yet
            new_task.user = request.user # Associate the task with the authenticated user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            # Handle invalid form input
            return render(request,'create_task.html',{
                'form': CreateTasks(),
                'error': 'Please provide valid data'
            })

# Log out the authenticated user
@login_required
def signout(request):
    logout(request)
    return redirect('home')

# User login view
def signin(request):
    if request.method == 'GET':
        # Display the login form
        return render(request,'signin.html',{
            'form': AuthenticationForm()
        })
    else:
        # Authenticate the user with form credentials
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])

        if not user is None:
            login(request,user)
            return redirect('tasks')
        else:
            # Handle invalid login attempts
            return render(request,'signin.html',{
                'form': AuthenticationForm(),
                'error': 'Username or password is incorrect'
            })