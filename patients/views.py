from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from accounts.models import CustomUser
from accounts.forms import PatientRegistrationForm
from .models import PatientProfile, SymptomRecord, DiseasePrediction
from .forms import SymptomRecordForm
from .ai_service import predict_disease_with_ai


@login_required
def admin_dashboard(request):
    """Admin dashboard - view all patients"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('patient_dashboard')
    
    patients = CustomUser.objects.filter(user_type='patient').select_related('patientprofile')

    search_query = request.GET.get('search', '')
    
    if search_query:
        patients = patients.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    context = {
        'patients': patients,
        'total_patients': CustomUser.objects.filter(user_type='patient').count(),
        'search_query': search_query,
    }
    return render(request, 'patients/admin_dashboard.html', context)


@login_required
def register_patient(request):
    """Admin can register new patients"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('patient_dashboard')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'patient'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            profile = PatientProfile.objects.create(
                user=user,
                registered_by=request.user
            )
            
            messages.success(request, f'Patient {user.get_full_name()} registered successfully!')
            return redirect('add_symptoms', patient_id=user.id)
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'patients/register_patient.html', {'form': form})


@login_required
def add_symptoms(request, patient_id):
    """Admin adds symptoms for a specific patient"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('patient_dashboard')
    
    patient = get_object_or_404(CustomUser, id=patient_id, user_type='patient')
    existing_symptoms = SymptomRecord.objects.filter(patient=patient)
    
    if request.method == 'POST':
        form = SymptomRecordForm(request.POST)
        if form.is_valid():
            symptom = form.save(commit=False)
            symptom.patient = patient
            symptom.recorded_by = request.user
            symptom.save()
            messages.success(request, f'Symptom "{symptom.symptom_name}" added successfully!')
            
            action = request.POST.get('action')
            if action == 'add_more':
                return redirect('add_symptoms', patient_id=patient_id)
            elif action == 'generate_prediction':
                return redirect('generate_prediction', patient_id=patient_id)
    else:
        form = SymptomRecordForm()
    
    return render(request, 'patients/add_symptoms.html', {
        'form': form,
        'patient': patient,
        'existing_symptoms': existing_symptoms,
    })


@login_required
def generate_prediction(request, patient_id):
    """Generate disease prediction using AI"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('patient_dashboard')
    
    patient = get_object_or_404(CustomUser, id=patient_id, user_type='patient')
    symptoms = SymptomRecord.objects.filter(patient=patient)
    
    if not symptoms.exists():
        messages.error(request, 'No symptoms recorded for this patient. Please add symptoms first.')
        return redirect('add_symptoms', patient_id=patient_id)
    
    if request.method == 'POST':
        symptom_list = []
        for symptom in symptoms:
            symptom_list.append({
                'name': symptom.symptom_name,
                'severity': symptom.get_severity_display(),
                'duration': symptom.duration_days
            })
        
        try:
            result, ai_response = predict_disease_with_ai(
                symptoms_list=symptom_list,
                patient_age=patient.age or 30,
                patient_gender=patient.gender,
                duration_days=max([s.duration_days for s in symptoms])
            )
            
            prediction = DiseasePrediction.objects.create(
                patient=patient,
                predicted_disease=result.get('primary_diagnosis', 'Unknown'),
                confidence_score=result.get('confidence_percentage', 0),
                risk_level=result.get('risk_level', 'medium'),
                symptoms_analyzed=symptom_list,
                recommendations='\n'.join(result.get('lifestyle_recommendations', [])),
                further_diagnostics='\n'.join(result.get('recommended_tests', [])),
                specialist_referral=result.get('specialist_referral', ''),
                ai_response=ai_response,
                predicted_by=request.user
            )
            
            messages.success(request, 'Disease prediction generated successfully!')
            return redirect('view_prediction', prediction_id=prediction.id)
            
        except Exception as e:
            messages.error(request, f'Error generating prediction: {str(e)}')
            return redirect('add_symptoms', patient_id=patient_id)
    
    return render(request, 'patients/generate_prediction.html', {
        'patient': patient,
        'symptoms': symptoms,
    })


@login_required
def view_prediction(request, prediction_id):
    """View detailed prediction results"""
    prediction = get_object_or_404(DiseasePrediction, id=prediction_id)
    
    if request.user.user_type == 'patient' and prediction.patient != request.user:
        messages.error(request, 'Access denied.')
        return redirect('patient_dashboard')
    
    try:
        import json
        ai_data = json.loads(prediction.ai_response)
    except:
        ai_data = {}
    
    return render(request, 'patients/view_prediction.html', {
        'prediction': prediction,
        'ai_data': ai_data,
    })


@login_required
def patient_dashboard(request):
    """Patient dashboard - view own health records"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied. Patient only.')
        return redirect('admin_dashboard')
    
    try:
        profile = PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        profile = PatientProfile.objects.create(user=request.user)
    
    symptoms = SymptomRecord.objects.filter(patient=request.user).order_by('-recorded_date')
    predictions = DiseasePrediction.objects.filter(patient=request.user).order_by('-prediction_date')
    
    return render(request, 'patients/patient_dashboard.html', {
        'profile': profile,
        'symptoms': symptoms,
        'predictions': predictions,
        'latest_prediction': predictions.first() if predictions.exists() else None,
        'total_symptoms': symptoms.count(),
        'total_predictions': predictions.count(),
    })


@login_required
def view_patient(request, patient_id):
    """Admin views detailed patient information"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('patient_dashboard')
    
    patient = get_object_or_404(CustomUser, id=patient_id, user_type='patient')
    profile = get_object_or_404(PatientProfile, user=patient)
    symptoms = SymptomRecord.objects.filter(patient=patient)
    predictions = DiseasePrediction.objects.filter(patient=patient)
    
    return render(request, 'patients/view_patient.html', {
        'patient': patient,
        'profile': profile,
        'symptoms': symptoms,
        'predictions': predictions,
    })


@login_required
@require_http_methods(["POST"])
def delete_symptom(request, symptom_id):
    """Delete a symptom record"""
    symptom = get_object_or_404(SymptomRecord, id=symptom_id)
    
    if request.user.user_type == 'admin' or symptom.patient == request.user:
        patient_id = symptom.patient.id
        symptom.delete()
        messages.success(request, 'Symptom deleted successfully.')
        
        if request.user.user_type == 'admin':
            return redirect('add_symptoms', patient_id=patient_id)
    else:
        messages.error(request, 'Access denied.')
    
    return redirect('patient_dashboard')
