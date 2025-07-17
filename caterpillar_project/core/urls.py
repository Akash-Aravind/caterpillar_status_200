from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Operator
    path('operator/home/', views.operator_home, name='operator_home'),
    path('operator/machines/', views.machine_conditions, name='machine_conditions'),

    # Assigner
    path('assigner/home/', views.assigner_home, name='assigner_home'),
    path('assigner/machines/', views.assigner_machine_conditions, name='assigner_machines'),

    path('assign-task/', views.assign_task, name='assign_task'),
    path('assigner/task-entry/', views.task_entry_view, name='task_entry'),

    path('operator/task/<int:task_id>/done/', views.mark_task_done, name='mark_task_done'),
    path('machine/<int:machine_id>/', views.machine_efficiency_view, name='machine_efficiency'),

]
