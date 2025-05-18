from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')

    def is_admin(self):
        return self.role == 'admin'

    def is_staff_user(self):
        return self.role == 'staff'


class Drug(models.Model):
    name = models.CharField(max_length=200)
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=200, blank=True)

    added_by = models.ForeignKey(User, related_name='drugs_added', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='drugs_updated', on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Batch: {self.batch_number})"


class Sale(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) # price per unit
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_sold = models.DateField(auto_now_add=True)

    created_by = models.ForeignKey(User, related_name='sales_made', on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_debtor(self):
        return self.amount_paid < self.total_amount

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity_sold * self.sale_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity_sold} x {self.drug.name} on {self.date_sold}"


from django.db import models
from django.utils import timezone  # ✅ Import this

class Debtor(models.Model):
    drug = models.ForeignKey('Drug', on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(max_length=100, blank=True)
    date_sold = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.drug.name} - {self.total_amount} TZS"

# models.py

from django.db import models

class Acknowledgement(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='acknowledgements/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Investor(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='investors/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

from django.db import models

class Investor(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='investors/')

class Acknowledgement(models.Model):
    description = models.TextField()
    image = models.ImageField(upload_to='acknowledgements/')
