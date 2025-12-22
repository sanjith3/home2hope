from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import Task, Item, TaskPhoto, LocationLog
from .forms import TaskCreationForm, TaskCompletionForm, ItemForm, TaskPhotoForm
from django.forms import modelformset_factory

from django.http import HttpResponse
import csv

@login_required
def dashboard(request):
    if request.user.role == 'ADMIN' or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.role == 'DRIVER':
        return redirect('driver_dashboard')
    return redirect('login')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.role == 'ADMIN' or self.request.user.is_superuser)

class DriverRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'DRIVER'

# ADMIN VIEWS
class AdminDashboardView(AdminRequiredMixin, View):
    def get(self, request):
        total_tasks = Task.objects.count()
        pending_tasks = Task.objects.exclude(status='COMPLETED').count()
        urgent_tasks = Task.objects.filter(is_urgent=True, status__in=['ASSIGNED', 'IN_PROGRESS']).count()
        completed_tasks = Task.objects.filter(status='COMPLETED').count()
        
        # Recent tasks
        recent_tasks = Task.objects.order_by('-created_at')[:5]
        
        context = {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'urgent_tasks': urgent_tasks,
            'completed_tasks': completed_tasks,
            'recent_tasks': recent_tasks,
        }
        return render(request, 'core/dashboard_admin.html', context)

class TaskCreateView(AdminRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreationForm
    template_name = 'core/task_form.html'
    success_url = reverse_lazy('admin_dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if not form.instance.assigned_to:
            form.instance.is_broadcast = True
        messages.success(self.request, "Task created successfully.")
        return super().form_valid(form)

class TaskListView(AdminRequiredMixin, ListView):
    model = Task
    template_name = 'core/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        filter_type = self.request.GET.get('filter')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        if filter_type == 'pending':
            queryset = queryset.exclude(status='COMPLETED')
        elif filter_type == 'urgent':
            queryset = queryset.filter(is_urgent=True)
        elif filter_type == 'completed':
            queryset = queryset.filter(status='COMPLETED')
            
        return queryset.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get('status')
        context['is_assigned'] = (status == 'ASSIGNED')
        context['is_in_progress'] = (status == 'IN_PROGRESS')
        context['is_completed'] = (status == 'COMPLETED')
        return context

class TaskHistoryView(AdminRequiredMixin, ListView):
    model = Task
    template_name = 'core/task_history.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.filter(status='COMPLETED')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
            
        return queryset.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
class AdminTaskDetailView(AdminRequiredMixin, DetailView):
    model = Task
    template_name = 'core/task_detail_admin.html'
    context_object_name = 'task'

class ExportTasksView(AdminRequiredMixin, View):
    def get(self, request):
        status = request.GET.get('status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        tasks = Task.objects.all().select_related('assigned_to').prefetch_related('items')

        if status:
            tasks = tasks.filter(status=status)
        if start_date:
            tasks = tasks.filter(created_at__date__gte=start_date)
        if end_date:
            tasks = tasks.filter(created_at__date__lte=end_date)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tasks_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Donor', 'Address', 'Status', 'Driver', 'Items Collected', 'Created At'])

        for task in tasks:
            items_str = ", ".join([f"{i.quantity} {i.category}" for i in task.items.all()])
            driver = task.assigned_to.username if task.assigned_to else 'Unassigned'
            writer.writerow([task.id, task.donor_name, task.address, task.get_status_display(), driver, items_str, task.created_at])

        return response

        return response

from django.contrib.auth.hashers import make_password
from .models import User

class DriverListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'core/driver_list.html'
    context_object_name = 'drivers'

    def get_queryset(self):
        return User.objects.filter(role='DRIVER')

class DriverCreateView(AdminRequiredMixin, CreateView):
    model = User
    fields = ['username', 'password', 'phone_number']
    template_name = 'core/driver_form.html'
    success_url = reverse_lazy('driver_list')

    def form_valid(self, form):
        form.instance.role = 'DRIVER'
        form.instance.password = make_password(form.cleaned_data['password'])
        messages.success(self.request, "Driver created successfully.")
        return super().form_valid(form)

class DriverDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        driver = get_object_or_404(User, pk=pk, role='DRIVER')
        if driver == request.user or driver.is_superuser:
            messages.error(request, "You cannot delete yourself or a superuser.")
            return redirect('driver_list')
            
        driver.delete()
        messages.success(request, "Driver removed successfully.")
        return redirect('driver_list')

# DRIVER VIEWS
class DriverDashboardView(DriverRequiredMixin, ListView):
    model = Task
    template_name = 'core/dashboard_driver.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Sort by Urgent first, then Created At
        return Task.objects.filter(
            Q(assigned_to=self.request.user) | Q(is_broadcast=True)
        ).exclude(status='COMPLETED').order_by('-is_urgent', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all tasks for this driver (including completed)
        all_tasks = Task.objects.filter(Q(assigned_to=self.request.user) | Q(is_broadcast=True))
        context['total_tasks'] = all_tasks.count()
        context['in_progress_tasks'] = all_tasks.filter(status='IN_PROGRESS').count()
        context['completed_tasks'] = all_tasks.filter(status='COMPLETED').count()
        return context

class DriverTaskDetailView(DriverRequiredMixin, DetailView):
    model = Task
    template_name = 'core/task_detail_driver.html'

    def get_queryset(self):
        return Task.objects.filter(Q(assigned_to=self.request.user) | Q(is_broadcast=True))

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        action = request.POST.get('action')
        
        if action == 'start_task':
            # Claim the task if it was broadcast
            if task.is_broadcast:
                task.is_broadcast = False
                task.assigned_to = request.user

            task.status = 'IN_PROGRESS'
            task.save()
            
            # Save location
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                LocationLog.objects.create(
                    task=task,
                    latitude=lat,
                    longitude=lng,
                    event='START'
                )
            messages.info(request, "Task started.")
            return redirect('driver_task_detail', pk=task.pk)
            
        return redirect('driver_task_detail', pk=task.pk)

@login_required
def complete_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    
    ItemFormSet = modelformset_factory(Item, form=ItemForm, extra=1, can_delete=True)
    PhotoFormSet = modelformset_factory(TaskPhoto, form=TaskPhotoForm, extra=1, can_delete=True)

    if request.method == 'POST':
        task_form = TaskCompletionForm(request.POST, instance=task)
        item_formset = ItemFormSet(request.POST, queryset=Item.objects.none())
        photo_formset = PhotoFormSet(request.POST, request.FILES, queryset=TaskPhoto.objects.none()) # Using none because creating new ones

        if task_form.is_valid() and item_formset.is_valid() and photo_formset.is_valid():
            task_form.save()
            
            instances = item_formset.save(commit=False)
            for instance in instances:
                instance.task = task
                instance.save()
            
            photos = photo_formset.save(commit=False)
            for photo in photos:
                photo.task = task
                photo.save()

            task.status = 'COMPLETED'
            task.completed_at = timezone.now()
            task.save()
            
            # Save location
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                LocationLog.objects.create(
                    task=task,
                    latitude=lat,
                    longitude=lng,
                    event='COMPLETE'
                )
            
            messages.success(request, "Task completed successfully!")
            item_formset = ItemFormSet(queryset=Item.objects.none())
            photo_formset = PhotoFormSet(queryset=TaskPhoto.objects.none())

            return redirect('receipt_view', pk=task.pk)
    else:
        task_form = TaskCompletionForm(instance=task)
        item_formset = ItemFormSet(queryset=Item.objects.none())
        photo_formset = PhotoFormSet(queryset=TaskPhoto.objects.none())

    return render(request, 'core/task_completion.html', {
        'task': task,
        'task_form': task_form,
        'item_formset': item_formset,
        'photo_formset': photo_formset
    })

@login_required
def receipt_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Check permission (either admin/superuser or the driver who did it)
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or task.assigned_to == request.user):
         return redirect('login') # Or 403

    items = task.items.all()
    # Simple formatting for WhatsApp
    # "Donation Receipt - Donor: [Name] - Items: [List...]"
    wa_text = f"Donation Receipt - Donor: {task.donor_name}. Items: "
    item_strings = [f"{i.quantity} {i.category}" for i in items]
    wa_text += ", ".join(item_strings)
    wa_text += ". Thank you!"
    
    context = {
        'task': task,
        'items': items,
        'wa_text': wa_text,
        'photos': task.photos.all(),
    }
    return render(request, 'core/receipt.html', context)
