# pylint: disable=import-error
# type: ignore
import json
from django.conf import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def predict_disease_with_ai(symptoms_list, patient_age, patient_gender, duration_days):
    """Use Google Gemini API to predict disease based on symptoms"""
    
    print("\n" + "="*60)
    print("[Gemini AI] Starting prediction...")
    print("="*60)
    
    if not GEMINI_AVAILABLE:
        print("[ERROR] google-generativeai not installed")
        return {
            "primary_diagnosis": "Module Missing",
            "confidence_percentage": 0,
            "risk_level": "medium",
            "explanation": "Install: pip install google-generativeai",
            "recommended_tests": ["Install module"],
            "lifestyle_recommendations": ["Run pip install"],
            "specialist_referral": "System Admin",
            "when_to_seek_care": "After installation"
        }, "Module not found"
    
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    print(f"[Gemini AI] API Key present: {bool(api_key)}")
    
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not set in settings")
        return {
            "primary_diagnosis": "Configuration Error",
            "confidence_percentage": 0,
            "risk_level": "medium",
            "explanation": "Add GEMINI_API_KEY to .env file",
            "recommended_tests": ["Configure .env"],
            "lifestyle_recommendations": ["Set API key"],
            "specialist_referral": "System Admin",
            "when_to_seek_care": "After configuration"
        }, "API Key not configured"
    
    try:
        print(f"[Gemini AI] Key starts with: {api_key[:20]}...")
        genai.configure(api_key=api_key)
        print("[Gemini AI] API configured successfully")
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        print("[Gemini AI] Model loaded: gemini-1.5-pro-latest")
        
        symptoms_text = ", ".join([f"{s['name']} (severity: {s['severity']}, {s['duration']} days)" 
                                   for s in symptoms_list])
        print(f"[Gemini AI] Symptoms: {symptoms_text}")
        
        prompt = f"""You are a medical AI assistant. Analyze these symptoms and provide assessment in JSON format:

Patient: {patient_age} years old, {patient_gender}
Symptoms: {symptoms_text}

Provide response in this exact JSON format:
{{
    "primary_diagnosis": "Most likely disease name",
    "confidence_percentage": 75,
    "risk_level": "low/medium/high/critical",
    "explanation": "Brief medical explanation",
    "recommended_tests": ["Test 1", "Test 2"],
    "lifestyle_recommendations": ["Advice 1", "Advice 2"],
    "specialist_referral": "Type of specialist",
    "when_to_seek_care": "When to visit doctor"
}}

IMPORTANT: Return ONLY valid JSON, no other text."""
        
        print("[Gemini AI] Sending request to Gemini API...")
        response = model.generate_content(prompt)
        ai_response = response.text
        
        print(f"[Gemini AI] Got response ({len(ai_response)} chars)")
        print(f"[Gemini AI] Response preview: {ai_response[:150]}...")
        
        json_start = ai_response.find('{')
        json_end = ai_response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            print("[Gemini AI] No JSON braces found, searching in lines...")
            lines = ai_response.split('\n')
            found = False
            for i, line in enumerate(lines):
                if '{' in line and '}' in line:
                    print(f"[Gemini AI] Found JSON in line {i}")
                    json_start = line.find('{')
                    json_end = line.rfind('}') + 1
                    ai_response = line[json_start:json_end]
                    found = True
                    break
            
            if not found:
                print("[ERROR] No JSON found in any line")
                raise ValueError("No JSON found in response")
        else:
            ai_response = ai_response[json_start:json_end]
        
        print(f"[Gemini AI] Extracted JSON: {ai_response[:100]}...")
        result = json.loads(ai_response)
        
        print(f"[Gemini AI] SUCCESS! Diagnosis: {result.get('primary_diagnosis')}")
        print("="*60 + "\n")
        return result, ai_response
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed: {str(e)}")
        print(f"[ERROR] Raw response was: {ai_response}")
        return {
            "primary_diagnosis": "Parse Error",
            "confidence_percentage": 0,
            "risk_level": "medium",
            "explanation": f"Failed to parse response: {str(e)}",
            "recommended_tests": ["Try again"],
            "lifestyle_recommendations": ["Contact support"],
            "specialist_referral": "Technical Support",
            "when_to_seek_care": "After fixing"
        }, f"Parse Error: {str(e)}"
    
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "primary_diagnosis": "Error",
            "confidence_percentage": 0,
            "risk_level": "medium",
            "explanation": f"Error: {type(e).__name__}: {str(e)}",
            "recommended_tests": ["Check logs"],
            "lifestyle_recommendations": ["Consult doctor"],
            "specialist_referral": "General Practitioner",
            "when_to_seek_care": "ASAP"
        }, f"Error: {str(e)}"
