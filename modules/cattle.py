from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
import cv2
import numpy as np
from PIL import Image
import base64
import io
import random
from . import db

cattle_bp = Blueprint('cattle', __name__, template_folder='../templates/cattle')

# Define Cattle model
class Cattle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_number = db.Column(db.String(50), unique=True, nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default='active')  # active, sold, deceased
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Float, nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    last_checkup = db.Column(db.DateTime, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

# AI Disease Database (Comprehensive data for AI-driven diagnosis)
DISEASE_DATABASE = {
    'foot_mouth_disease': {
        'name': 'Foot and Mouth Disease',
        'symptoms': ['blisters on tongue', 'drooling', 'fever', 'limping', 'reduced appetite', 'salivation', 'blisters on feet', 'lameness'],
        'treatment': 'Isolate animal, provide supportive care, contact veterinarian immediately',
        'severity': 'high',
        'contagious': True,
        'prevention': 'Vaccination, biosecurity measures, quarantine new animals',
        'recovery_time': '2-3 weeks',
        'visual_indicators': ['mouth lesions', 'foot lesions', 'excessive salivation']
    },
    'mastitis': {
        'name': 'Mastitis',
        'symptoms': ['swollen udder', 'abnormal milk', 'fever', 'reduced appetite', 'pain in udder', 'hardened udder', 'discolored milk', 'flakes in milk'],
        'treatment': 'Antibiotics, milking hygiene, warm compresses, frequent milking',
        'severity': 'medium',
        'contagious': False,
        'prevention': 'Proper milking hygiene, clean housing, regular udder checks',
        'recovery_time': '5-14 days',
        'visual_indicators': ['swollen udder', 'abnormal milk color', 'udder redness']
    },
    'pneumonia': {
        'name': 'Bovine Pneumonia',
        'symptoms': ['coughing', 'nasal discharge', 'fever', 'difficulty breathing', 'rapid breathing', 'lethargy', 'loss of appetite', 'depression'],
        'treatment': 'Antibiotics, anti-inflammatories, rest, proper ventilation',
        'severity': 'medium',
        'contagious': True,
        'prevention': 'Vaccination, good ventilation, reduce stress',
        'recovery_time': '1-3 weeks',
        'visual_indicators': ['nasal discharge', 'labored breathing', 'extended neck while breathing']
    },
    'bloat': {
        'name': 'Bloat',
        'symptoms': ['swollen left side', 'difficulty breathing', 'restlessness', 'discomfort', 'excessive salivation', 'rapid breathing', 'kicking at belly'],
        'treatment': 'Emergency veterinary care, trocar insertion, stomach tube',
        'severity': 'high',
        'contagious': False,
        'prevention': 'Proper feeding management, avoid sudden diet changes',
        'recovery_time': '1-2 days with treatment',
        'visual_indicators': ['distended left abdomen', 'signs of discomfort', 'labored breathing']
    },
    'bvd': {
        'name': 'Bovine Viral Diarrhea (BVD)',
        'symptoms': ['diarrhea', 'fever', 'nasal discharge', 'oral erosions', 'reduced appetite', 'depression', 'weight loss', 'reproductive issues'],
        'treatment': 'Supportive care, fluids, antibiotics for secondary infections',
        'severity': 'high',
        'contagious': True,
        'prevention': 'Vaccination, testing and removal of persistently infected animals',
        'recovery_time': '2-3 weeks',
        'visual_indicators': ['diarrhea', 'nasal discharge', 'mouth lesions']
    },
    'johnes_disease': {
        'name': 'Johne\'s Disease',
        'symptoms': ['chronic diarrhea', 'weight loss', 'normal appetite', 'reduced milk production', 'bottle jaw'],
        'treatment': 'No effective treatment, management to reduce spread',
        'severity': 'high',
        'contagious': True,
        'prevention': 'Testing and culling, calf management, biosecurity',
        'recovery_time': 'Incurable',
        'visual_indicators': ['emaciation despite eating', 'watery diarrhea', 'swelling under jaw']
    },
    'laminitis': {
        'name': 'Laminitis',
        'symptoms': ['lameness', 'reluctance to walk', 'heat in hooves', 'pain response to hoof pressure', 'abnormal stance', 'shifting weight'],
        'treatment': 'Dietary changes, pain management, hoof trimming, soft bedding',
        'severity': 'medium',
        'contagious': False,
        'prevention': 'Proper nutrition, avoid grain overload, regular hoof care',
        'recovery_time': '1-2 weeks to months depending on severity',
        'visual_indicators': ['abnormal hoof growth', 'reluctance to move', 'standing with weight shifted to heels']
    },
    'milk_fever': {
        'name': 'Milk Fever (Hypocalcemia)',
        'symptoms': ['weakness', 'cold ears', 'muscle tremors', 'inability to stand', 'collapse', 'reduced body temperature'],
        'treatment': 'Calcium supplementation, IV calcium gluconate',
        'severity': 'high',
        'contagious': False,
        'prevention': 'Proper pre-calving diet, calcium supplementation',
        'recovery_time': '24-48 hours with treatment',
        'visual_indicators': ['downer cow', 'muscle tremors', 'S-shaped neck']
    },
    'ketosis': {
        'name': 'Ketosis',
        'symptoms': ['reduced appetite', 'decreased milk production', 'weight loss', 'sweet-smelling breath', 'neurological signs', 'lethargy'],
        'treatment': 'Glucose or propylene glycol administration, IV dextrose',
        'severity': 'medium',
        'contagious': False,
        'prevention': 'Proper transition cow management, body condition monitoring',
        'recovery_time': '3-5 days with treatment',
        'visual_indicators': ['dullness', 'weight loss', 'abnormal behavior']
    },
    'tuberculosis': {
        'name': 'Bovine Tuberculosis',
        'symptoms': ['chronic cough', 'weight loss', 'swollen lymph nodes', 'weakness', 'fluctuating fever', 'reduced milk production'],
        'treatment': 'Usually culling due to zoonotic potential',
        'severity': 'high',
        'contagious': True,
        'prevention': 'Testing and culling, biosecurity, import controls',
        'recovery_time': 'Typically not treated',
        'visual_indicators': ['emaciation', 'enlarged lymph nodes', 'chronic respiratory signs']
    }
}

# Nutrition recommendations database
NUTRITION_DATABASE = {
    'holstein': {
        'milk_production': {
            'high': {'protein': 18, 'energy': 75, 'fiber': 25, 'feed_mix': 'High protein concentrate with quality hay'},
            'medium': {'protein': 16, 'energy': 70, 'fiber': 28, 'feed_mix': 'Balanced concentrate with good roughage'},
            'low': {'protein': 14, 'energy': 65, 'fiber': 30, 'feed_mix': 'Maintenance ration with adequate roughage'}
        }
    },
    'jersey': {
        'milk_production': {
            'high': {'protein': 17, 'energy': 70, 'fiber': 26, 'feed_mix': 'Quality concentrate with legume hay'},
            'medium': {'protein': 15, 'energy': 65, 'fiber': 29, 'feed_mix': 'Standard dairy ration'},
            'low': {'protein': 13, 'energy': 60, 'fiber': 32, 'feed_mix': 'Basic maintenance feed'}
        }
    },
    'gir': {
        'milk_production': {
            'high': {'protein': 16, 'energy': 68, 'fiber': 27, 'feed_mix': 'Local concentrate with fresh fodder'},
            'medium': {'protein': 14, 'energy': 62, 'fiber': 30, 'feed_mix': 'Traditional feed with green fodder'},
            'low': {'protein': 12, 'energy': 58, 'fiber': 33, 'feed_mix': 'Grazing with minimal supplementation'}
        }
    }
}

@cattle_bp.route('/')
def index():
    # Get all cattle from database
    cattle_list = Cattle.query.all()
    
    # Format for display
    cattle_data = []
    for cow in cattle_list:
        cattle_data.append({
            'id': cow.id,
            'tag_number': cow.tag_number,
            'breed': cow.breed,
            'gender': cow.gender,
            'age': calculate_age(cow.date_of_birth) if cow.date_of_birth else 'Unknown',
            'weight': cow.weight,
            'status': cow.status,
            'image': cow.image_filename
        })
    
    # Add missing variables for the template
    total_cattle = len(cattle_list)
    healthy_cattle = sum(1 for cow in cattle_list if cow.status == 'active')
    total_milk_production = 120.5  # Example value, replace with actual calculation if available
    avg_milk_production = total_milk_production / total_cattle if total_cattle > 0 else 0
    
    return render_template('cattle/index.html', 
                          cattle=cattle_data,
                          total_cattle=total_cattle,
                          healthy_cattle=healthy_cattle,
                          total_milk_production=total_milk_production,
                          avg_milk_production=avg_milk_production)

# Helper function to calculate age
def calculate_age(birth_date, in_years=False, is_year=None):
    # Handle is_year parameter for backward compatibility
    if is_year is not None:
        in_years = is_year
        
    if not birth_date:
        return 'Unknown' if not in_years else 0
    today = datetime.today().date()
    age_days = (today - birth_date).days
    
    if in_years:
        return age_days / 365
        
    if age_days < 30:
        return f"{age_days} days"
    elif age_days < 365:
        months = age_days // 30
        return f"{months} months"
    else:
        years = age_days // 365
        months = (age_days % 365) // 30
        if months > 0:
            return f"{years} years, {months} months"
        return f"{years} years"

@cattle_bp.route('/add', methods=['GET', 'POST'])
def add_cattle():
    if request.method == 'POST':
        from app import db, Cattle
        
        try:
            cattle = Cattle(
                tag_number=request.form['tag_number'],
                breed=request.form['breed'],
                age=int(request.form['age']),
                weight=float(request.form['weight']),
                health_status=request.form.get('health_status', 'Healthy'),
                milk_yield_daily=float(request.form.get('milk_yield_daily', 0))
            )
            
            db.session.add(cattle)
            db.session.commit()
            
            flash('Cattle added successfully!', 'success')
            return redirect(url_for('cattle.index'))
            
        except Exception as e:
            flash(f'Error adding cattle: {str(e)}', 'error')
    
    return render_template('cattle/add.html')

@cattle_bp.route('/view/<int:cattle_id>')
def view_cattle(cattle_id):
    from app import Cattle, HealthRecord
    
    cattle = Cattle.query.get_or_404(cattle_id)
    health_records = HealthRecord.query.filter_by(animal_type='cattle', animal_id=cattle_id).order_by(HealthRecord.record_date.desc()).all()
    
    # Generate lifecycle data
    basic_lifecycle_data = generate_lifecycle_data(cattle)
    detailed_lifecycle_data = generate_detailed_lifecycle_data(cattle)
    
    return render_template('cattle/view.html', 
                         cattle=cattle, 
                         health_records=health_records,
                         lifecycle_data=basic_lifecycle_data,
                         detailed_lifecycle_data=detailed_lifecycle_data)

@cattle_bp.route('/health-check', methods=['GET', 'POST'])
def health_check():
    from app import Cattle, HealthRecord, db
    
    # Get all cattle for dropdown selection
    cattle_list = Cattle.query.all()
    
    if request.method == 'POST':
        # Handle image upload
        if 'cattle_image' in request.files:
            file = request.files['cattle_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cattle', filename)
                file.save(filepath)
                
                # Get symptoms from form
                symptoms_text = request.form.get('symptoms', '')
                
                # Get selected symptoms from checkboxes
                selected_symptoms = []
                for symptom in ['fever', 'coughing', 'limping', 'diarrhea', 'loss_appetite', 
                               'nasal_discharge', 'swollen_udder', 'abnormal_behavior']:
                    if request.form.get(symptom):
                        selected_symptoms.append(request.form.get(symptom))
                
                # Combine text symptoms with selected symptoms
                all_symptoms = symptoms_text
                if selected_symptoms:
                    all_symptoms += ", " + ", ".join(selected_symptoms)
                
                # Get cattle ID if selected
                cattle_id = request.form.get('cattle_id')
                cattle_info = None
                if cattle_id:
                    cattle_info = Cattle.query.get(cattle_id)
                
                # Simulate AI analysis using our comprehensive function
                analysis_result = simulate_ai_analysis(filepath, all_symptoms, cattle_info)
                
                # Check if there was an error in analysis
                if 'error' in analysis_result:
                    flash(f"Error in analysis: {analysis_result['error']}", 'danger')
                    return render_template('cattle/health_check.html', cattle_list=cattle_list)
                
                # Save health record if a cattle was selected
                if cattle_id:
                    health_record = HealthRecord(
                        animal_type='cattle',
                        animal_id=cattle_id,
                        record_type='disease',
                        details=f"AI detected: {analysis_result['diagnosis']['name']} (Confidence: {analysis_result['diagnosis']['confidence']:.1f}%)",
                        date=datetime.now()
                    )
                    db.session.add(health_record)
                    db.session.commit()
                
                return render_template('cattle/health_check_result.html', 
                                     analysis_result=analysis_result,
                                     image_path=f'uploads/cattle/{filename}',
                                     cattle_info=cattle_info)
        else:
            flash("Please upload an image for analysis", 'warning')
    
    return render_template('cattle/health_check.html', cattle_list=cattle_list)

@cattle_bp.route('/nutrition-recommendation', methods=['GET', 'POST'])
def nutrition_recommendation():
    if request.method == 'POST':
        breed = request.form['breed'].lower()
        milk_yield = float(request.form['milk_yield'])
        body_weight = float(request.form['body_weight'])
        
        # Get additional parameters if provided
        age = request.form.get('age')
        age = float(age) if age else None
        
        activity_level = request.form.get('activity_level', 'moderate')
        pregnancy_status = request.form.get('pregnancy_status', 'not_pregnant')
        environmental_temp = request.form.get('environmental_temp')
        environmental_temp = float(environmental_temp) if environmental_temp else None
        
        # Determine production level
        if milk_yield > 20:
            production_level = 'high'
        elif milk_yield > 10:
            production_level = 'medium'
        else:
            production_level = 'low'
        
        # Get nutrition recommendation
        if breed in NUTRITION_DATABASE:
            nutrition_info = NUTRITION_DATABASE[breed]['milk_production'][production_level]
        else:
            # Default to Holstein recommendations
            nutrition_info = NUTRITION_DATABASE['holstein']['milk_production'][production_level]
        
        # Calculate daily requirements
        feed_amount = body_weight * 0.03  # 3% of body weight
        
        # Adjust feed amount based on activity level
        activity_multipliers = {
            'low': 0.9,
            'moderate': 1.0,
            'high': 1.15
        }
        feed_amount *= activity_multipliers.get(activity_level, 1.0)
        
        # Adjust for pregnancy status
        if pregnancy_status == 'early_pregnancy':
            feed_amount *= 1.05
        elif pregnancy_status == 'mid_pregnancy':
            feed_amount *= 1.1
        elif pregnancy_status == 'late_pregnancy':
            feed_amount *= 1.15
        
        # Adjust for environmental temperature
        if environmental_temp is not None:
            if environmental_temp < 5:  # Cold weather
                feed_amount *= 1.1
            elif environmental_temp > 30:  # Hot weather
                feed_amount *= 0.95
        
        # Calculate concentrate amount based on milk yield
        concentrate_amount = milk_yield * 0.5  # 500g per liter of milk
        
        # Adjust concentrate for high-producing cows
        if production_level == 'high':
            concentrate_amount *= 1.1
        
        # Calculate water requirement (liters per day)
        water_requirement = body_weight * 0.1 + milk_yield * 1.5
        
        # Generate special recommendations based on conditions
        special_recommendations = []
        
        if age is not None and age > 10:
            special_recommendations.append("For older cattle, consider adding joint supplements and reducing grain content.")
        
        if environmental_temp is not None and environmental_temp > 30:
            special_recommendations.append("In hot weather, provide shade and increase water availability by 20%. Feed during cooler parts of the day.")
        elif environmental_temp is not None and environmental_temp < 5:
            special_recommendations.append("In cold weather, increase energy density of ration and ensure water sources don't freeze.")
        
        if pregnancy_status == 'late_pregnancy':
            special_recommendations.append("For late-pregnancy cows, gradually transition to a pre-calving diet with proper DCAD balance.")
        
        # Generate AI insight based on all parameters
        ai_insight = generate_ai_nutrition_insight(breed, production_level, milk_yield, body_weight, age, activity_level, pregnancy_status, environmental_temp)
        
        recommendation = {
            'breed': breed.title(),
            'production_level': production_level.title(),
            'daily_feed_amount': round(feed_amount, 1),
            'concentrate_amount': round(concentrate_amount, 1),
            'nutrition_info': nutrition_info,
            'additional_tips': generate_nutrition_tips(breed, production_level),
            'milk_yield': milk_yield,
            'body_weight': body_weight,
            'water_requirement': round(water_requirement, 1),
            'age': age,
            'activity_level': activity_level,
            'pregnancy_status': pregnancy_status,
            'environmental_temp': environmental_temp,
            'special_recommendations': special_recommendations,
            'ai_insight': ai_insight
        }
        
        return render_template('cattle/nutrition_result.html', recommendation=recommendation)
    
    return render_template('cattle/nutrition_recommendation.html')

# AI-driven Disease Symptom Checker
def simulate_ai_analysis(image_path, symptoms_text, cattle_info=None):
    """Simulate AI analysis of cattle health based on image and symptoms"""
    try:
        # Load and process the image
        img = cv2.imread(image_path)
        if img is None:
            return {'error': 'Failed to load image'}
        
        # Convert symptoms to lowercase for matching
        symptoms_text = symptoms_text.lower()
        
        # Extract individual symptoms from text
        symptom_keywords = [
            'fever', 'cough', 'limping', 'lameness', 'diarrhea', 'appetite', 'nasal', 'discharge',
            'swollen', 'udder', 'breathing', 'difficulty', 'blisters', 'drooling', 'salivation',
            'weight loss', 'abnormal milk', 'restlessness', 'tremors', 'collapse', 'weakness'
        ]
        
        # Detect symptoms from text
        detected_symptoms = []
        for keyword in symptom_keywords:
            if keyword in symptoms_text:
                detected_symptoms.append(keyword)
        
        # Perform image analysis (simulated)
        visual_symptoms = simulate_image_analysis(img)
        
        # Combine detected symptoms from text and image
        all_symptoms = list(set(detected_symptoms + visual_symptoms))
        
        # Match symptoms to diseases
        matched_diseases = match_symptoms_to_diseases(all_symptoms)
        
        # Get the most likely disease
        if matched_diseases:
            primary_diagnosis = matched_diseases[0]
            confidence = primary_diagnosis['match_score']
            disease_info = DISEASE_DATABASE[primary_diagnosis['disease_id']]
            
            # Generate recommendations based on diagnosis
            recommendations = generate_recommendations(disease_info, cattle_info)
            
            # Create detailed analysis result
            analysis_result = {
                'diagnosis': {
                    'name': disease_info['name'],
                    'confidence': confidence,
                    'severity': disease_info['severity'],
                    'contagious': disease_info['contagious'],
                    'treatment': disease_info['treatment'],
                    'prevention': disease_info.get('prevention', 'No specific prevention information available'),
                    'recovery_time': disease_info.get('recovery_time', 'Varies')
                },
                'detected_symptoms': {
                    'from_text': detected_symptoms,
                    'from_image': visual_symptoms,
                    'matched': [s for s in all_symptoms if s in ' '.join(disease_info['symptoms'])]
                },
                'differential_diagnosis': [
                    {
                        'name': DISEASE_DATABASE[d['disease_id']]['name'],
                        'confidence': d['match_score'],
                        'key_symptoms': [s for s in all_symptoms if s in ' '.join(DISEASE_DATABASE[d['disease_id']]['symptoms'])]
                    } for d in matched_diseases[1:3] if d['match_score'] > 30
                ],
                'recommendations': recommendations,
                'ai_notes': generate_ai_notes(disease_info, all_symptoms)
            }
            
            return analysis_result
        else:
            return {
                'diagnosis': {
                    'name': 'Inconclusive',
                    'confidence': 0,
                    'severity': 'unknown',
                    'contagious': False,
                    'treatment': 'Consult with a veterinarian for proper diagnosis',
                    'prevention': 'Regular health checks',
                    'recovery_time': 'Unknown'
                },
                'detected_symptoms': {
                    'from_text': detected_symptoms,
                    'from_image': visual_symptoms,
                    'matched': []
                },
                'differential_diagnosis': [],
                'recommendations': ['Consult with a veterinarian for proper diagnosis',
                                  'Monitor the animal closely for any changes in symptoms',
                                  'Ensure proper nutrition and hydration'],
                'ai_notes': 'Insufficient symptoms detected to make a confident diagnosis. Please consult with a veterinarian.'
            }
    
    except Exception as e:
        return {'error': str(e)}

# Helper functions for AI analysis
def simulate_image_analysis(img):
    """Simulate detecting visual symptoms from image"""
    # In a real implementation, this would use computer vision models
    # For simulation, we'll randomly detect some visual symptoms
    
    # Convert to HSV for color analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Get image dimensions and basic statistics
    height, width, _ = img.shape
    avg_color = np.mean(img, axis=(0, 1))
    
    # Simulate detection based on image properties
    visual_symptoms = []
    
    # Detect redness (potential inflammation)
    red_mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
    red_ratio = np.count_nonzero(red_mask) / (height * width)
    if red_ratio > 0.05:  # Threshold for detection
        visual_symptoms.append('redness')
        visual_symptoms.append('inflammation')
    
    # Detect swelling (simulated by blob detection)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 5:  # Arbitrary threshold
        visual_symptoms.append('swelling')
    
    # Randomly detect some symptoms for demonstration
    # In a real system, these would be detected by trained models
    possible_visual_symptoms = [
        'blisters', 'swollen udder', 'nasal discharge', 'limping',
        'abnormal stance', 'labored breathing', 'mouth lesions'
    ]
    
    # Randomly select 0-2 symptoms for demonstration
    num_random_symptoms = random.randint(0, 2)
    random_symptoms = random.sample(possible_visual_symptoms, num_random_symptoms)
    visual_symptoms.extend(random_symptoms)
    
    return visual_symptoms

def match_symptoms_to_diseases(symptoms):
    """Match detected symptoms to diseases in the database"""
    matches = []
    
    # Convert symptoms list to a single string for easier matching
    symptoms_text = ' '.join(symptoms).lower()
    
    for disease_id, disease_info in DISEASE_DATABASE.items():
        # Calculate match score based on symptom overlap
        match_score = 0
        matched_symptoms = 0
        
        # Check each disease symptom against detected symptoms
        for disease_symptom in disease_info['symptoms']:
            if disease_symptom.lower() in symptoms_text:
                matched_symptoms += 1
                # Key symptoms get higher weight
                if disease_symptom in disease_info.get('visual_indicators', []):
                    match_score += 15  # Higher weight for visual indicators
                else:
                    match_score += 10
        
        # Add base score for any match
        if matched_symptoms > 0:
            # Calculate percentage of disease symptoms matched
            symptom_coverage = matched_symptoms / len(disease_info['symptoms'])
            # Adjust score based on coverage
            match_score = match_score * (0.5 + 0.5 * symptom_coverage)
            
            matches.append({
                'disease_id': disease_id,
                'match_score': match_score,
                'matched_symptoms': matched_symptoms,
                'total_symptoms': len(disease_info['symptoms'])
            })
    
    # Sort by match score (highest first)
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    return matches

def generate_recommendations(disease_info, cattle_info):
    """Generate tailored recommendations based on diagnosis and cattle info"""
    recommendations = []
    
    # Basic recommendations based on disease
    if disease_info['severity'] == 'high':
        recommendations.append('Contact veterinarian immediately')
    else:
        recommendations.append('Schedule veterinary consultation')
    
    # Add treatment recommendation
    recommendations.append(f'Treatment: {disease_info["treatment"]}')
    
    # Add prevention recommendation
    if 'prevention' in disease_info:
        recommendations.append(f'Prevention: {disease_info["prevention"]}')
    
    # Add isolation recommendation if contagious
    if disease_info['contagious']:
        recommendations.append('Isolate affected animal from the herd')
        recommendations.append('Monitor other animals for similar symptoms')
    
    # Add cattle-specific recommendations if info available
    if cattle_info:
        if cattle_info.milk_yield_daily > 0:
            recommendations.append('Monitor milk production closely')
            if 'mastitis' in disease_info['name'].lower():
                recommendations.append('Discard milk until treatment is complete')
        
        # Age-specific recommendations
        if cattle_info.age < 2:
            recommendations.append('Young animals may need more intensive care')
        elif cattle_info.age > 8:
            recommendations.append('Older animals may need extended recovery time')
    
    return recommendations

def generate_ai_notes(disease_info, detected_symptoms):
    """Generate additional AI insights about the condition"""
    notes = []
    
    # Add notes about disease severity
    if disease_info['severity'] == 'high':
        notes.append('This is a serious condition requiring immediate attention.')
    
    # Add notes about contagion risk
    if disease_info['contagious']:
        notes.append('This is a contagious condition that poses risk to other animals.')
    
    # Add notes about symptom patterns
    disease_symptoms = set([s.lower() for s in disease_info['symptoms']])
    detected_set = set([s.lower() for s in detected_symptoms])
    
    # Calculate overlap and missing symptoms
    overlap = disease_symptoms.intersection(detected_set)
    missing = disease_symptoms - detected_set
    
    if len(overlap) > 0:
        notes.append(f'Key matching symptoms: {", ".join(list(overlap)[:3])}')
    
    if len(missing) > 0:
        notes.append(f'Watch for additional symptoms: {", ".join(list(missing)[:3])}')
    
    # Add recovery expectation
    if 'recovery_time' in disease_info:
        notes.append(f'Expected recovery time with proper treatment: {disease_info["recovery_time"]}')
    
    return ' '.join(notes)

@cattle_bp.route('/lifecycle-tracker/<int:cattle_id>')
def lifecycle_tracker(cattle_id):
    from app import Cattle
    
    try:
        cattle = Cattle.query.get_or_404(cattle_id)
        lifecycle_data = generate_detailed_lifecycle_data(cattle)
    except Exception as e:
        print(f"Error in lifecycle_tracker: {e}")
        cattle = None
        lifecycle_data = None
    
    return render_template('cattle/lifecycle_tracker_dashboard.html', 
                         cattle=cattle, 
                         lifecycle_data=lifecycle_data)

@cattle_bp.route('/anomaly-detection', methods=['GET', 'POST'])
def anomaly_detection():
    if request.method == 'POST':
        if 'herd_image' in request.files:
            file = request.files['herd_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cattle', filename)
                file.save(filepath)
                
                # Simulate anomaly detection
                anomalies = simulate_anomaly_detection(filepath)
                
                return render_template('cattle/anomaly_result.html', 
                                     anomalies=anomalies,
                                     image_path=f'uploads/cattle/{filename}')
    
    return render_template('cattle/anomaly_detection.html')

@cattle_bp.route('/genetic-traits/<int:cattle_id>')
def genetic_traits(cattle_id):
    from app import Cattle
    
    cattle = Cattle.query.get_or_404(cattle_id)
    
    # Simulate genetic trait analysis
    genetic_data = {
        'milk_production_genes': {
            'DGAT1': 'AA (High milk fat)',
            'ABCG2': 'AB (Moderate protein)',
            'GHR': 'BB (High yield potential)'
        },
        'health_traits': {
            'disease_resistance': 85,
            'fertility_index': 92,
            'longevity_score': 78
        },
        'breeding_recommendations': generate_breeding_recommendations(cattle),
        'offspring_predictions': generate_offspring_predictions(cattle)
    }
    
    return render_template('cattle/genetic_traits.html', 
                         cattle=cattle, 
                         genetic_data=genetic_data)

# Helper functions
def simulate_ai_analysis(image_path, symptoms):
    """Simulate AI analysis of cattle image and symptoms"""
    
    # Simulate image processing
    detected_symptoms = []
    
    # Parse input symptoms
    input_symptoms = [s.strip().lower() for s in symptoms.split(',') if s.strip()]
    
    # Match symptoms to diseases
    possible_diseases = []
    for disease_id, disease_info in DISEASE_DATABASE.items():
        match_score = 0
        for symptom in input_symptoms:
            for db_symptom in disease_info['symptoms']:
                if symptom in db_symptom or db_symptom in symptom:
                    match_score += 1
        
        if match_score > 0:
            possible_diseases.append({
                'disease': disease_info,
                'confidence': min(match_score * 25, 95),  # Max 95% confidence
                'matched_symptoms': match_score
            })
    
    # Sort by confidence
    possible_diseases.sort(key=lambda x: x['confidence'], reverse=True)
    
    # If no diseases matched, suggest healthy status
    if not possible_diseases:
        return {
            'status': 'Healthy',
            'confidence': 95,
            'diseases': [],
            'recommendations': ['Regular monitoring', 'Maintain good nutrition', 'Schedule routine checkup']
        }
    
    return {
        'status': 'Requires Attention' if possible_diseases[0]['confidence'] > 70 else 'Monitoring Needed',
        'confidence': possible_diseases[0]['confidence'],
        'diseases': possible_diseases[:3],  # Top 3 matches
        'recommendations': generate_health_recommendations(possible_diseases[0]['disease'])
    }

def generate_health_recommendations(disease_info):
    """Generate health recommendations based on disease"""
    recommendations = [disease_info['treatment']]
    
    if disease_info['contagious']:
        recommendations.append('Isolate the animal immediately')
        recommendations.append('Disinfect equipment and housing')
    
    if disease_info['severity'] == 'high':
        recommendations.append('Contact veterinarian immediately')
    else:
        recommendations.append('Monitor condition closely')
    
    return recommendations

def generate_lifecycle_data(cattle):
    """Generate lifecycle tracking data"""
    current_age = cattle.age * 365  # Convert to days
    
    stages = []
    if current_age < 730:  # Less than 2 years
        stages.append({'stage': 'Calf', 'start': 0, 'end': 365, 'status': 'completed' if current_age > 365 else 'current'})
        stages.append({'stage': 'Heifer', 'start': 365, 'end': 730, 'status': 'current' if current_age > 365 and current_age <= 730 else 'pending'})
    else:
        stages.append({'stage': 'Calf', 'start': 0, 'end': 365, 'status': 'completed'})
        stages.append({'stage': 'Heifer', 'start': 365, 'end': 730, 'status': 'completed'})
        stages.append({'stage': 'Milking Cow', 'start': 730, 'end': current_age + 1000, 'status': 'current'})
    
    return {
        'current_stage': next((s['stage'] for s in stages if s['status'] == 'current'), 'Unknown'),
        'stages': stages,
        'age_days': current_age,
        'estimated_productive_years': max(0, 12 - cattle.age)
    }

def generate_detailed_lifecycle_data(cattle):
    """Generate detailed lifecycle data"""
    return {
        'current_phase': determine_current_phase(cattle),
        'milestones': generate_milestones(cattle),
        'performance_metrics': calculate_performance_metrics(cattle),
        'future_projections': generate_future_projections(cattle)
    }

def determine_current_phase(cattle):
    if cattle.age < 2:
        return 'Heifer'
    elif cattle.age < 8:
        return 'Productive'
    else:
        return 'Senior'

def generate_milestones(cattle):
    milestones = [
        {'event': 'Birth', 'date': calculate_birth_date(cattle.age), 'status': 'completed'},
        {'event': 'First Heat', 'date': calculate_event_date(cattle.age, 15), 'status': 'completed' if cattle.age > 1.5 else 'pending'},
        {'event': 'First Breeding', 'date': calculate_event_date(cattle.age, 18), 'status': 'completed' if cattle.age > 2 else 'pending'},
        {'event': 'First Calving', 'date': calculate_event_date(cattle.age, 27), 'status': 'completed' if cattle.age > 2.5 else 'pending'},
    ]
    return milestones

def calculate_birth_date(age):
    return (datetime.now() - timedelta(days=age * 365)).strftime('%Y-%m-%d')

def calculate_event_date(current_age, event_age_months):
    event_date = datetime.now() - timedelta(days=current_age * 365) + timedelta(days=event_age_months * 30)
    return event_date.strftime('%Y-%m-%d')

@cattle_bp.route('/lifecycle-tracker-dashboard', methods=['GET', 'POST'])
def lifecycle_tracker_dashboard():
    from app import Cattle
    
    # Get all cattle for dropdown selection
    try:
        cattle_list = Cattle.query.all()
        selected_cattle = None
        lifecycle_data = None
        detailed_lifecycle_data = None
        
        if request.method == 'POST':
            cattle_id = request.form.get('cattle_id')
            if cattle_id:
                selected_cattle = Cattle.query.get_or_404(int(cattle_id))
                lifecycle_data = generate_lifecycle_data(selected_cattle)
                detailed_lifecycle_data = generate_detailed_lifecycle_data(selected_cattle)
    except Exception as e:
        print(f"Error in lifecycle_tracker_dashboard: {e}")
        cattle_list = []
        selected_cattle = None
        lifecycle_data = None
        detailed_lifecycle_data = None
    
    return render_template('cattle/lifecycle_tracker_dashboard.html',
                         cattle_list=cattle_list,
                         selected_cattle=selected_cattle,
                         lifecycle_data=lifecycle_data,
                         detailed_lifecycle_data=detailed_lifecycle_data)

def calculate_performance_metrics(cattle):
    return {
        'lifetime_milk_production': cattle.milk_yield_daily * cattle.age * 305 if cattle.milk_yield_daily else 0,  # Assuming 305-day lactation
        'average_daily_production': cattle.milk_yield_daily or 0,
        'reproductive_efficiency': random.randint(80, 95),
        'health_score': 95 if cattle.health_status == 'Healthy' else 70
    }

def generate_future_projections(cattle):
    return {
        'projected_lifetime_production': cattle.milk_yield_daily * (12 - cattle.age) * 305 if cattle.milk_yield_daily and cattle.age < 12 else 0,
        'estimated_calves': max(0, (12 - cattle.age) * 0.8),
        'retirement_age': 12,
        'economic_value': calculate_economic_value(cattle)
    }

def calculate_economic_value(cattle):
    if cattle.milk_yield_daily:
        annual_milk_value = cattle.milk_yield_daily * 305 * 50  # ₹50 per liter
        remaining_years = max(0, 12 - cattle.age)
        return annual_milk_value * remaining_years
    return 0

def generate_nutrition_tips(breed, production_level):
    """Generate nutrition tips based on breed and production level"""
    common_tips = [
        "Ensure clean, fresh water is available at all times",
        "Introduce any feed changes gradually over 1-2 weeks",
        "Monitor body condition score monthly and adjust feeding accordingly",
        "Provide adequate bunk space to ensure all animals can eat simultaneously"
    ]
    
    breed_specific_tips = {
        'holstein': {
            'high': [
                "Split concentrate feeding into 3-4 smaller meals throughout the day",
                "Include buffer supplements to prevent ruminal acidosis",
                "Consider protected fat supplements to support milk production"
            ],
            'medium': [
                "Balance energy and protein carefully to maintain production",
                "Ensure adequate fiber to maintain rumen health"
            ],
            'low': [
                "Focus on quality forage to meet maintenance requirements",
                "Limit concentrates to prevent excessive weight gain"
            ]
        },
        'jersey': {
            'high': [
                "Provide higher fat content in diet to support milk fat production",
                "Monitor body condition closely as Jerseys can lose condition rapidly"
            ],
            'medium': [
                "Balance energy density to match their efficient feed conversion",
                "Ensure adequate mineral supplementation for milk quality"
            ],
            'low': [
                "Focus on maintaining optimal body condition",
                "Provide quality forage with minimal concentrates"
            ]
        },
        'gir': {
            'high': [
                "Supplement with locally available protein sources",
                "Ensure heat stress management during hot weather"
            ],
            'medium': [
                "Balance traditional feeding practices with nutritional requirements",
                "Incorporate seasonal green fodder when available"
            ],
            'low': [
                "Utilize grazing efficiently with strategic supplementation",
                "Focus on maintaining health and condition with minimal inputs"
            ]
        }
    }
    
    # Get breed-specific tips or default to holstein if breed not found
    if breed in breed_specific_tips:
        breed_tips = breed_specific_tips[breed][production_level]
    else:
        breed_tips = breed_specific_tips['holstein'][production_level]
    
    # Combine common and breed-specific tips
    all_tips = common_tips + breed_tips
    
    return all_tips

def generate_ai_nutrition_insight(breed, production_level, milk_yield, body_weight, age, activity_level, pregnancy_status, environmental_temp):
    """Generate AI insight based on all cattle parameters"""
    
    insights = [
        f"This nutrition plan is optimized for {breed.title()} cattle with {production_level} milk production.",
        f"The feed-to-milk conversion efficiency is approximately {round(body_weight/milk_yield, 1)}:1 for this animal."
    ]
    
    # Add age-specific insights
    if age is not None:
        if age < 3:
            insights.append("Young cattle still have growth requirements in addition to production needs.")
        elif age > 8:
            insights.append("Older cattle may benefit from easier-to-digest feed components and joint supplements.")
    
    # Add activity level insights
    if activity_level == 'high':
        insights.append("Higher activity levels require additional energy to maintain body condition while supporting milk production.")
    
    # Add pregnancy insights
    if pregnancy_status != 'not_pregnant':
        insights.append("Pregnant cattle need additional nutrients to support fetal development while maintaining production.")
    
    # Add temperature insights
    if environmental_temp is not None:
        if environmental_temp > 25:
            insights.append("In warmer conditions, consider feeding during cooler parts of the day and increasing water availability.")
        elif environmental_temp < 10:
            insights.append("Cold weather increases maintenance energy requirements to maintain body temperature.")
    
    # Select one primary insight and one secondary insight
    if len(insights) > 2:
        selected_insights = [insights[0], random.choice(insights[1:])] 
        return " ".join(selected_insights)
    else:
        return " ".join(insights)

def simulate_anomaly_detection(image_path):
    """Simulate anomaly detection in herd images"""
    
    # Generate mock anomalies
    anomalies = []
    
    # Random number of anomalies (0-3)
    num_anomalies = random.randint(0, 3)
    
    possible_anomalies = [
        {'type': 'Underweight Animal', 'severity': 'medium', 'description': 'Detected animal showing signs of weight loss'},
        {'type': 'Limping', 'severity': 'high', 'description': 'Animal showing unusual gait pattern'},
        {'type': 'Isolation Behavior', 'severity': 'medium', 'description': 'Animal separated from herd'},
        {'type': 'Abnormal Posture', 'severity': 'low', 'description': 'Unusual standing or lying position'},
        {'type': 'Skin Condition', 'severity': 'medium', 'description': 'Possible skin lesions or irritation detected'}
    ]
    
    for i in range(num_anomalies):
        anomaly = random.choice(possible_anomalies)
        anomaly['confidence'] = random.randint(75, 95)
        anomaly['location'] = f"Animal #{random.randint(1, 10)}"
        anomalies.append(anomaly)
        possible_anomalies.remove(anomaly)  # Avoid duplicates
    
    return anomalies

def generate_breeding_recommendations(cattle):
    """Generate breeding recommendations based on cattle data"""
    
    recommendations = []
    
    if cattle.breed.lower() == 'holstein':
        recommendations = [
            "Breed with Jersey bull for improved fat content",
            "Consider AI from proven high milk yield sires",
            "Focus on fertility and longevity traits"
        ]
    elif cattle.breed.lower() == 'jersey':
        recommendations = [
            "Breed with Holstein for increased milk volume",
            "Select for improved protein percentage",
            "Consider heat tolerance traits"
        ]
    else:  # Indigenous breeds
        recommendations = [
            "Crossbreed with Holstein for increased yield",
            "Maintain heat tolerance characteristics",
            "Focus on disease resistance traits"
        ]
    
    return recommendations

def generate_offspring_predictions(cattle):
    """Generate predicted offspring characteristics"""
    
    base_yield = cattle.milk_yield_daily or 15
    
    predictions = [
        {
            'trait': 'Milk Yield',
            'expected_range': f"{base_yield * 0.8:.1f} - {base_yield * 1.2:.1f} liters/day",
            'confidence': 85
        },
        {
            'trait': 'Adult Weight',
            'expected_range': f"{cattle.weight * 0.9:.0f} - {cattle.weight * 1.1:.0f} kg",
            'confidence': 80
        },
        {
            'trait': 'Health Score',
            'expected_range': "Good to Excellent",
            'confidence': 75
        }
    ]
    
    return predictions

@cattle_bp.route('/reports')
def cattle_reports():
    """Generate reports for cattle management"""
    from app import Cattle, HealthRecord
    
    # Get all cattle
    cattle_list = Cattle.query.all()
    
    # Generate report data
    total_cattle = len(cattle_list)
    active_cattle = sum(1 for cow in cattle_list if cow.status == 'active')
    
    # Calculate average weight and age
    weights = [cow.weight for cow in cattle_list if cow.weight]
    avg_weight = sum(weights) / len(weights) if weights else 0
    
    ages = [calculate_age(cow.date_of_birth, in_years=True) for cow in cattle_list if cow.date_of_birth]
    avg_age = sum(ages) / len(ages) if ages else 0
    
    # Get health records
    health_records = HealthRecord.query.filter_by(animal_type='cattle').order_by(HealthRecord.record_date.desc()).limit(50).all()
    
    # Generate breed distribution
    breed_distribution = {}
    for cow in cattle_list:
        if cow.breed in breed_distribution:
            breed_distribution[cow.breed] += 1
        else:
            breed_distribution[cow.breed] = 1
    
    # Generate monthly milk production (mock data)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    milk_production = [random.randint(800, 1200) for _ in range(12)]
    
    return render_template('cattle/reports.html',
                         total_cattle=total_cattle,
                         active_cattle=active_cattle,
                         avg_weight=avg_weight,
                         avg_age=avg_age,
                         health_records=health_records,
                         breed_distribution=breed_distribution,
                         months=months,
                         milk_production=milk_production)

@cattle_bp.route('/schedule')
def cattle_schedule():
    """Schedule management for cattle"""
    from app import Cattle
    from .calendar_module import CalendarEvent
    
    # Get all cattle
    cattle_list = Cattle.query.all()
    
    # Get upcoming events for cattle
    upcoming_events = CalendarEvent.query.filter(
        CalendarEvent.title.like('%cattle%') | 
        CalendarEvent.notes.like('%cattle%') | 
        CalendarEvent.location.like('%cattle%')
    ).filter(
        CalendarEvent.event_date >= datetime.today().date()
    ).order_by(CalendarEvent.event_date).limit(10).all()
    
    return render_template('cattle/schedule.html',
                         cattle_list=cattle_list,
                         upcoming_events=upcoming_events)
