import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import User

# Create Admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    admin.role = 'ADMIN'
    admin.save()
    print("Created Admin user: admin/adminpass")

# Create Driver
if not User.objects.filter(username='driver').exists():
    driver = User.objects.create_user('driver', 'driver@example.com', 'driverpass')
    driver.role = 'DRIVER'
    driver.save()
    print("Created Driver user: driver/driverpass")
