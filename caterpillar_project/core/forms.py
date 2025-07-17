from django import forms
from .models import Task, Machine, Operator

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=Operator.objects.all(),
        label="Assign to Operator"
    )
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Deadline"
    )
    machines = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.none(),  # will be set dynamically in view
        widget=forms.CheckboxSelectMultiple,
        label="Select Machines"
    )

    class Meta:
        model = Task
        fields = [
            'assigned_to',
            'title',
            'description',
            'deadline',
            'machines',
            'task_type',
            'terrain_type',
            'material',
            'task_complexity',
            'accessibility_level',
            'shift',
            'activity_level'
        ]
