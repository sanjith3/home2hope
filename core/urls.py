from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Admin
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/history/', views.TaskHistoryView.as_view(), name='task_history'),
    path('tasks/<int:pk>/admin/', views.AdminTaskDetailView.as_view(), name='admin_task_detail'),
    path('tasks/<int:pk>/cancel/', views.TaskCancelView.as_view(), name='task_cancel'),
    path('tasks/<int:pk>/reset/', views.TaskResetView.as_view(), name='task_reset'),
    path('tasks/export/', views.ExportTasksView.as_view(), name='task_export'),
    path('tasks/pdf/', views.TaskPDFView.as_view(), name='task_pdf_report'),
    
    # Driver Management (Admin)
    path('drivers/', views.DriverListView.as_view(), name='driver_list'),
    path('drivers/add/', views.DriverCreateView.as_view(), name='driver_create'),
    path('drivers/<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver_delete'),
    
    # Driver Interface
    path('my-tasks/', views.DriverDashboardView.as_view(), name='driver_dashboard'),
    path('task/<int:pk>/', views.DriverTaskDetailView.as_view(), name='driver_task_detail'),
    path('task/<int:pk>/complete/', views.complete_task_view, name='task_complete'),
    
    # Receipt
    path('receipt/<int:pk>/', views.receipt_view, name='receipt_view'),
]
