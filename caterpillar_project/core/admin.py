from django.contrib import admin
from .models import Machine,Operator,Assigner,Task

admin.site.register(Machine)
admin.site.register(Operator)
admin.site.register(Assigner)
admin.site.register(Task)