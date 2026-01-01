from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_DRIVER = 'DRIVER'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_DRIVER, 'Driver'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_DRIVER)
    phone_number = models.CharField(max_length=20, blank=True)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_driver(self):
        return self.role == self.ROLE_DRIVER

class Task(models.Model):
    STATUS_ASSIGNED = 'ASSIGNED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    donor_name = models.CharField(max_length=255)
    address = models.TextField()
    phone_numbers = models.CharField(max_length=255, help_text="Comma-separated phone numbers")
    location_link = models.URLField(max_length=500, help_text="Google Maps Share Link")
    
    CATEGORY_CHOICES = [
        ('FURNITURE', 'Furniture'),
        ('CLOTHES', 'Clothes'),
        ('ELECTRONICS', 'Electronics'),
        ('FOOD', 'Food'),
        ('BOOKS', 'Books'),
        ('OTHER', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHER')
    qty = models.PositiveIntegerField(null=True,blank=True)
    is_urgent = models.BooleanField(default=False)
    is_broadcast = models.BooleanField(default=False, help_text="If true, this task is visible to all drivers until assigned")
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ASSIGNED)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # New fields based on completion form
    visitor_form_filled = models.BooleanField(default=False)
    trust_notice_given = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.donor_name} - {self.status}- {self.qty }"

class Item(models.Model):
    CONDITION_GOOD = 'GOOD'
    CONDITION_AVERAGE = 'AVERAGE'
    CONDITION_POOR = 'POOR'
    CONDITION_CHOICES = [
        (CONDITION_GOOD, 'Good'),
        (CONDITION_AVERAGE, 'Average'),
        (CONDITION_POOR, 'Poor'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='items')
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default=CONDITION_GOOD)

    def __str__(self):
        return f"{self.quantity} x {self.category} ({self.condition})"

class TaskPhoto(models.Model):
    PHOTO_TYPE_ITEM = 'ITEM'
    PHOTO_TYPE_DONOR = 'DONOR'
    PHOTO_TYPE_VISITOR_FORM = 'VISITOR_FORM'
    PHOTO_TYPE_OTHER = 'OTHER'
    PHOTO_TYPE_CHOICES = [
        (PHOTO_TYPE_ITEM, 'Item Photo'),
        (PHOTO_TYPE_DONOR, 'Donor Photo'),
        (PHOTO_TYPE_VISITOR_FORM, 'Visitor Form'),
        (PHOTO_TYPE_OTHER, 'Other'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='task_photos/%Y/%m/%d/')
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPE_CHOICES, default=PHOTO_TYPE_ITEM)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class LocationLog(models.Model):
    EVENT_START = 'START'
    EVENT_COMPLETE = 'COMPLETE'
    EVENT_CHOICES = [
        (EVENT_START, 'Task Started'),
        (EVENT_COMPLETE, 'Task Completed'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='location_logs')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
