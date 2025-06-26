from django.urls import path
from . import views

# Application route definitions
urlpatterns = [
    path('',views.home,name='home'), # Home page or landing page
    path('signup/',views.signup,name='signup'), # User registration page
    path('tasks/',views.tasks,name='tasks'), # User's task overview
    path('tasks_completed/',views.tasks_completed,name='tasks_completed'), # List of completed tasks
    path('tasks/create/',views.create_task,name='create_task'), # Form to create a new task
    path('tasks/<int:task_id>/',views.task_detail,name='task_detail'), # View and edit details of a specific task
    path('tasks/<int:task_id>/complete',views.complete_task,name='complete_task'), # Mark a task as completed
    path('tasks/<int:task_id>/delete',views.delete_task,name='delete_task'), # Delete a task
    path('signout/',views.signout,name='logout'), # User logout
    path('signin/',views.signin,name='signin') # User logout
]
