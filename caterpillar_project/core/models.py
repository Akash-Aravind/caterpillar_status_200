from django.db import models


class Operator(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Assigner(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Machine(models.Model):
    machine_id = models.CharField(max_length=50)
    machine_name = models.CharField(max_length=100)
    unique_identifier = models.CharField(max_length=100, unique=True)
    is_assigned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.machine_id} - {self.unique_identifier}"


class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ("Excavation", "Excavation"),
        ("Grading", "Grading"),
        ("Transport", "Transport"),
    ]

    TERRAIN_TYPE_CHOICES = [
        ("Flat", "Flat"),
        ("Sloped", "Sloped"),
        ("Uneven", "Uneven"),
        ("Rugged", "Rugged"),
    ]

    MATERIAL_CHOICES = [
        ("Soil", "Soil"),
        ("Sand", "Sand"),
        ("Gravel", "Gravel"),
        ("Debris", "Debris"),
        ("Concrete", "Concrete"),
    ]

    COMPLEXITY_CHOICES = [
        ("Simple", "Simple"),
        ("Moderate", "Moderate"),
        ("Complex", "Complex"),
    ]

    ACCESSIBILITY_CHOICES = [
        ("Easy", "Easy"),
        ("Moderate", "Moderate"),
        ("Difficult", "Difficult"),
    ]

    SHIFT_CHOICES = [
        ("Day", "Day"),
        ("Night", "Night"),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    assigned_to = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    machines = models.ManyToManyField(Machine)

    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default="Excavation")
    terrain_type = models.CharField(max_length=20, choices=TERRAIN_TYPE_CHOICES, default="Flat")
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default="Soil")
    task_complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default="Simple")
    accessibility_level = models.CharField(max_length=20, choices=ACCESSIBILITY_CHOICES, default="Easy")
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default="Day")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default="Medium")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
