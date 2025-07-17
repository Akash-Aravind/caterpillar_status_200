from django.shortcuts import render, redirect
from .models import Operator, Assigner,Machine, Task

from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from datetime import timedelta

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






        
def assigner_home(request):
    return render(request, 'assigner_home.html')

def machine_conditions(request):
    return render(request, 'machine_conditions.html')

def logout_view(request):
    return redirect('login')  # placeholder for now




from django.shortcuts import render
from .models import Machine
import numpy as np
import joblib
import os

def assigner_machine_conditions(request):
    machines = Machine.objects.all()

    model_path = os.path.join('models', 'machine_behaviour_efficiency.pkl')
    model = joblib.load(model_path)

    machine_data = []
    for machine in machines:
        input_data = np.array([
            [
                np.random.randint(650, 750),    # Engine Hours
                np.random.randint(110, 150),    # Fuel Used (L)
                np.random.randint(40, 70),      # Load Cycles
                np.random.randint(60, 90),      # Idling Time (min)
                np.random.randint(2100, 2500),  # Machine RPM
                np.random.randint(0, 2),        # Safety Alerts Triggered
                np.random.randint(0, 2),        # Proximity Hazards Detected
                np.random.randint(2000, 3000),  # Load Weight (kg)
                np.random.randint(75, 100)      # Fuel Tank Level (%)
            ]
        ])
        predicted_efficiency = model.predict(input_data)[0]
        machine_data.append({
            'id': machine.id,
            'unique_id': machine.unique_identifier,
            'name': machine.machine_name,
            'efficiency': f"{predicted_efficiency:.2f}%"
        })

    return render(request, 'assigner_machines.html', {'machine_data': machine_data})



def calculate_efficiency(machine):
    # Dummy logic — you must replace this with your real formula
    # For example:
    if machine.total_tasks == 0:
        return 0
    return round((machine.successful_tasks / machine.total_tasks) * 100, 2)


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





import joblib
import numpy as np
from django.shortcuts import get_object_or_404, render
from .models import Machine
import os

def machine_efficiency_view(request, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)

    # Load the trained model
    model_path = os.path.join('models', 'machine_behaviour_efficiency.pkl')
    model = joblib.load(model_path)


    # Random realistic input generation
    input_data = np.array([[
        np.random.randint(650, 700),    # weight - upper end
        np.random.randint(90, 110),     # duration - lower-mid
        np.random.randint(60, 80),      # depth - upper end
        np.random.randint(80, 100),     # width - upper end
        np.random.randint(2300, 2500),  # rpm - high
        1,                              # binary feature 1
        0,                              # binary feature 2
        np.random.randint(2700, 3000),  # torque - high
        np.random.randint(90, 100)      # temperature - high
    ]])

    # Predict efficiency (assumed to be a float percentage)
    predicted_efficiency = model.predict(input_data)[0]

    return render(request, 'machine_efficiency.html', {
        'machine': machine,
        'efficiency': f"{predicted_efficiency:.2f}%",
    })























# # views.py
# import os
# import pandas as pd
# import joblib,pickle  # or pickle depending on how the model was saved
# from django.shortcuts import render
# from django.conf import settings
# from django.http import HttpResponse

# # views.py
# import os
# import pandas as pd
# import joblib  # or joblib if used during saving
# from django.shortcuts import render
# from django.conf import settings
# from django.http import HttpResponse  # ✅ Required for returning text response

def test_anomaly_detector(request):
    pass
#     model_path = os.path.join(settings.BASE_DIR, 'models', 'anomaly_detector_model.pkl')

#     with open(model_path, 'rb') as f:
#         model = joblib.load(model_path)

#     # Input data (static test)
#     data = {
#         "Timestamp": ["2025-07-17 12:31:45.574228"],
#         "Machine ID": ["M7"],
#         "Machine Name": ["CAT CS74B Soil Compactor"],
#         "Operator ID": ["O3"],
#         "GPS Location": ["Zone B"],
#         "Engine Hours": [4382.4],
#         "Fuel Used (L)": [4.28],
#         "Load Cycles": [3],
#         "Idling Time (min)": [10],
#         "Machine RPM": [2651],
#         "Safety Alerts Triggered": [0],
#         "Proximity Hazards Detected": [0],
#         "Load Weight (kg)": [2619.4],
#         "Fuel Tank Level (%)": [79.7],
#         "Efficiency Score": [57.9625]
#     }

#     df = pd.DataFrame(data)

#     # ✅ Select only features used during training
#     features = [
#         "Engine Hours",
#         "Fuel Used (L)",
#         "Load Cycles",
#         "Idling Time (min)",
#         "Machine RPM",
#         "Safety Alerts Triggered",
#         "Proximity Hazards Detected",
#         "Load Weight (kg)",
#         "Fuel Tank Level (%)",
#         "Efficiency Score"
#     ]

#     df_model_input = df[features]

#     prediction = model.predict(df_model_input)

#     return HttpResponse(f"✅ Anomaly Prediction: {prediction[0]}")











import os
import pandas as pd
import joblib
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
from .models import Task, Operator

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Operator, Task
import os
import pandas as pd
import joblib
from django.conf import settings

# Load the trained regression model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'task_time_estimation.pkl')
model = joblib.load(MODEL_PATH)

# Expected input columns in the model
FEATURE_COLUMNS = [
    'Task Type', 'Task Complexity', 'Terrain', 'Material', 'Weather', 'Moisture',
    'Visibility', 'Temp (°C)', 'Accessibility', 'Shift', 'Lighting',
    'Support Crew', 'Activity'
]

# Mapping of feature name to model field name
FIELD_MAPPING = {
    'Task Type': 'task_type',
    'Task Complexity': 'task_complexity',
    'Terrain': 'terrain',
    'Material': 'material',
    'Weather': 'weather',
    'Moisture': 'moisture',
    'Visibility': 'visibility',
    'Temp (°C)': 'temperature',
    'Accessibility': 'accessibility',
    'Shift': 'shift',
    'Lighting': 'lighting',
    'Support Crew': 'support_crew',
    'Activity': 'activity'
}

# Static fallback values
STATIC_INPUT = {
    'Task Type': 'Excavation',
    'Task Complexity': 'Medium',
    'Terrain': 'Flat',
    'Material': 'Soil',
    'Weather': 'Clear',
    'Moisture': 'Normal',
    'Visibility': 'Good',
    'Temp (°C)': 27,
    'Accessibility': 'Moderate',
    'Shift': 'Day',
    'Lighting': 'Natural',
    'Support Crew': 'Yes',
    'Activity': 'Digging'
}

def operator_home(request):
    operator_id = request.session.get('operator_id')
    if not operator_id:
        return redirect('login')

    try:
        operator = Operator.objects.get(id=operator_id)
        tasks = Task.objects.filter(assigned_to=operator).order_by('deadline')

        enriched_tasks = []
        for task in tasks:
            input_data = {}

            for feature in FEATURE_COLUMNS:
                field_name = FIELD_MAPPING.get(feature)
                value = getattr(task, field_name, None)
                if value is None:
                    value = STATIC_INPUT[feature]
                input_data[feature] = value

            input_df = pd.DataFrame([input_data])
            predicted_duration = model.predict(input_df)[0]  # Assuming output in hours

            time_remaining = task.deadline - timezone.now()
            time_remaining_hours = time_remaining.total_seconds() / 3600  # Convert to hours

            alert = predicted_duration > time_remaining_hours

            enriched_tasks.append({
                "instance": task,
                "predicted_duration": round(predicted_duration, 2),
                'time_remaining': str(task.deadline - timezone.now()),
                "alert": alert
            })


        return render(request, 'operator_home.html', {
            'tasks': enriched_tasks,
            'operator': operator
        })

    except Operator.DoesNotExist:
        return render(request, 'operator_home.html', {'error': 'Operator not found'})
