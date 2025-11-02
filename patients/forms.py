from django import forms
from .models import SymptomRecord

# Simplified form - only for symptoms
class SymptomRecordForm(forms.ModelForm):
    class Meta:
        model = SymptomRecord
        fields = ['symptom_name', 'severity', 'duration_days', 'notes']
        widgets = {
            'symptom_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Fever, Cough, Headache'
            }),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Number of days'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Additional information (optional)'
            }),
        }
