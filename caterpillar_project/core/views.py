from django.shortcuts import render, redirect
from .models import Operator, Assigner,Machine, Task

from django.contrib.auth.decorators import login_required
from .forms import TaskForm


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        if role == 'operator':
            user = Operator.objects.filter(username=username, password=password).first()
            if user:
                request.session['operator_username'] = user.username
                request.session['operator_id'] = user.id  # ✅ Save operator ID in session
                return redirect('operator_home')

        elif role == 'assigner':
            user = Assigner.objects.filter(username=username, password=password).first()
            if user:
                request.session['assigner_username'] = user.username
                request.session['assigner_id'] = user.id  # ✅ Save assigner ID in session
                return redirect('assigner_home')

        elif role == 'admin':
            # Same logic if admin login is needed
            pass

    return render(request, 'login.html')




def signup_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if role == 'operator':
            Operator.objects.create(username=username, password=password)
            return redirect('login')
        elif role == 'assigner':
            Assigner.objects.create(username=username, password=password)
            return redirect('login')

    return render(request, 'signup.html')

def operator_home(request):
    operator_id = request.session.get('operator_id')

    if not operator_id:
        return redirect('login')  # or your custom operator login page

    try:
        operator = Operator.objects.get(id=operator_id)
        
        # Sort tasks by deadline
        tasks = Task.objects.filter(assigned_to=operator).order_by('deadline')
        
        return render(request, 'operator_home.html', {
            'tasks': tasks,
            'operator': operator
        })
        
    except Operator.DoesNotExist:
        return render(request, 'operator_home.html', {
            'error': 'Operator not found'
        })

        
def assigner_home(request):
    return render(request, 'assigner_home.html')

def machine_conditions(request):
    return render(request, 'machine_conditions.html')

def logout_view(request):
    return redirect('login')  # placeholder for now




def assigner_machine_conditions(request):
    return render(request, 'assigner_machines.html')




from .models import Operator, Assigner, Machine, Task

def assign_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        form.fields['machines'].queryset = get_available_machines()

        if form.is_valid():
            task = form.save(commit=False)
            
            # Fetch the logged-in Assigner manually since you're not using Django auth
            assigner_username = request.session.get('assigner_username')
            assigner = Assigner.objects.filter(username=assigner_username).first()
            
            task.assigned_by = assigner
            task.save()
            form.save_m2m()
            return redirect('assigner_home')
    else:
        form = TaskForm()
        form.fields['machines'].queryset = get_available_machines()

    return render(request, 'assign_task.html', {'form': form})

def get_available_machines():
    # Get machines that are not already assigned to a task
    assigned_machines = Machine.objects.filter(task__isnull=False)
    return Machine.objects.exclude(id__in=assigned_machines)



from django.shortcuts import render
from .models import Operator, Machine
from .forms import TaskForm


from .models import Operator, Machine
from .forms import TaskForm
from .views import get_available_machines  # import helper function
def task_entry_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        form.fields['machines'].queryset = get_available_machines()

        if form.is_valid():
            task = form.save(commit=False)

            assigner_username = request.session.get('assigner_username')
            assigner = Assigner.objects.filter(username=assigner_username).first()

            if not assigner:
                return render(request, 'task_entry.html', {
                    'form': form,
                    'error': 'Assigner not found in session'
                })

            task.assigned_by = assigner
            task.save()
            form.save_m2m()

            return redirect('assigner_home')  # ✅ Redirect after success
        else:
            print("Form errors:", form.errors)  # ✅ Debug
    else:
        form = TaskForm()
        form.fields['machines'].queryset = get_available_machines()

    return render(request, 'task_entry.html', {'form': form})



from django.shortcuts import redirect, get_object_or_404
from .models import Task

def mark_task_done(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)

        # Free up all machines assigned to this task
        for machine in task.machines.all():
            machine.is_assigned = False
            machine.save()

        # Delete the task
        task.delete()

        return redirect('operator_home')  # or wherever your dashboard is

    return redirect('operator_home')





from django.shortcuts import get_object_or_404
from .models import Machine

def machine_efficiency_view(request, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)
    # For now, just show dummy efficiency
    efficiency = "89%"  # You can replace this with real data later
    return render(request, 'machine_efficiency.html', {
        'machine': machine,
        'efficiency': efficiency,
    })