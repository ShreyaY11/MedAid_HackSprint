from django.contrib import admin
from .models import PatientProfile, SymptomRecord, DiseasePrediction

admin.site.register(PatientProfile)
admin.site.register(SymptomRecord)
admin.site.register(DiseasePrediction)
