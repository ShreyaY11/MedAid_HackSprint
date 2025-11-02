from django.urls import path
from . import views

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/register-patient/', views.register_patient, name='register_patient'),
    path('admin/patient/<int:patient_id>/', views.view_patient, name='view_patient'),
    path('admin/patient/<int:patient_id>/add-symptoms/', views.add_symptoms, name='add_symptoms'),
    path('admin/patient/<int:patient_id>/generate-prediction/', views.generate_prediction, name='generate_prediction'),
    
    # Patient URLs
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    # Shared URLs
    path('prediction/<int:prediction_id>/', views.view_prediction, name='view_prediction'),
    path('symptom/<int:symptom_id>/delete/', views.delete_symptom, name='delete_symptom'),
]
