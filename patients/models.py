from django.db import models
from django.conf import settings

class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patientprofile')
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    registration_date = models.DateTimeField(auto_now_add=True)
    medical_history = models.TextField(blank=True, help_text="Previous medical conditions")
    blood_group = models.CharField(max_length=5, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"Profile: {self.user.username}"
    
    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'


class SymptomRecord(models.Model):
    SEVERITY_CHOICES = [
        (1, 'Mild'),
        (2, 'Moderate'),
        (3, 'Severe'),
    ]
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='symptoms')
    symptom_name = models.CharField(max_length=200)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=2)
    duration_days = models.IntegerField(help_text="How many days has this symptom persisted?")
    recorded_date = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_symptoms')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.patient.username} - {self.symptom_name}"
    
    class Meta:
        ordering = ['-recorded_date']
        verbose_name = 'Symptom Record'
        verbose_name_plural = 'Symptom Records'


class DiseasePrediction(models.Model):
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='predictions')
    predicted_disease = models.CharField(max_length=200)
    confidence_score = models.FloatField(help_text="Confidence percentage (0-100)")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    symptoms_analyzed = models.JSONField(help_text="List of symptoms used for prediction")
    recommendations = models.TextField()
    further_diagnostics = models.TextField()
    specialist_referral = models.CharField(max_length=200, blank=True)
    prediction_date = models.DateTimeField(auto_now_add=True)
    ai_response = models.TextField(help_text="Full AI response in JSON format")
    predicted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='predictions_made')
    
    def __str__(self):
        return f"{self.patient.username} - {self.predicted_disease}"
    
    class Meta:
        ordering = ['-prediction_date']
        verbose_name = 'Disease Prediction'
        verbose_name_plural = 'Disease Predictions'
