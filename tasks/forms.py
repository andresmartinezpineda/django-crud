from django import forms
from .models import Task

# Form for creating or editing tasks based on the Task model
class CreateTasks(forms.ModelForm):
    class Meta:
        model = Task  # Model associated with the form
        fields = ['title','description','important']  # Fields to include in the form

        # Widget customization to improve frontend appearance and user experience
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control','placeholder': 'write a title'}),
            'description': forms.Textarea(attrs={'class': 'form-control','placeholder':'write a description'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'})
        }


