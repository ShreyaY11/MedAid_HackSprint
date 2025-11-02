from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (('admin', 'Admin'), ('patient', 'Patient'))
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, default='other')
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
