from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw
from . import db

fish_bp = Blueprint('fish', __name__, template_folder='../templates/fish')

# Define Fish model
class Fish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.String(50), unique=True, nullable=False)
    species = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=0)
    water_temperature = db.Column(db.Float, nullable=True)
    ph_level = db.Column(db.Float, nullable=True)
    oxygen_level = db.Column(db.Float, nullable=True)
    feed_type = db.Column(db.String(100), nullable=True)
    feed_rate = db.Column(db.Float, nullable=True)  # kg per day
    stocking_date = db.Column(db.Date, nullable=True)
    harvest_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    last_water_change = db.Column(db.DateTime, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

# Fish disease database
FISH_DISEASES = {
    'fungal_infection': {
        'name': 'Fungal Infection',
        'symptoms': ['white patches', 'cotton-like growth', 'lethargy'],
        'treatment': 'Antifungal treatment, improve water quality',
        'severity': 'medium'
    },
    'bacterial_infection': {
        'name': 'Bacterial Infection',
        'symptoms': ['fin rot', 'ulcers', 'red streaks'],
        'treatment': 'Antibiotics, water change',
        'severity': 'high'
    },
    'ich': {
        'name': 'White Spot Disease (Ich)',
        'symptoms': ['white spots', 'scratching', 'rapid breathing'],
        'treatment': 'Increase temperature, salt treatment',
        'severity': 'medium'
    }
}

@fish_bp.route('/')
def index():
    fish_ponds = Fish.query.all()
    total_ponds = len(fish_ponds)
    total_fish = sum([f.count for f in fish_ponds if f.count])
    
    # Calculate statistics
    avg_water_temp = sum([f.water_temperature for f in fish_ponds if f.water_temperature]) / total_ponds if total_ponds > 0 else 0
    avg_ph = sum([f.ph_level for f in fish_ponds if f.ph_level]) / total_ponds if total_ponds > 0 else 0
    
    return render_template('fish/index.html',
                         fish_ponds=fish_ponds,
                         total_ponds=total_ponds,
                         total_fish=total_fish,
                         avg_water_temp=avg_water_temp,
                         avg_ph=avg_ph)
                         
@fish_bp.route('/inventory')
def inventory():
    fish_ponds = Fish.query.all()
    total_ponds = len(fish_ponds)
    total_fish = sum([f.count for f in fish_ponds if f.count])
    
    # Calculate statistics
    avg_water_temp = sum([f.water_temperature for f in fish_ponds if f.water_temperature]) / total_ponds if total_ponds > 0 else 0
    avg_ph = sum([f.ph_level for f in fish_ponds if f.ph_level]) / total_ponds if total_ponds > 0 else 0
    
    return render_template('fish/inventory.html',
                         fish_ponds=fish_ponds,
                         total_ponds=total_ponds,
                         total_fish=total_fish,
                         avg_water_temp=avg_water_temp,
                         avg_ph=avg_ph)

@fish_bp.route('/add', methods=['GET', 'POST'])
def add_pond():
    if request.method == 'POST':
        from app import db, Fish
        
        try:
            fish = Fish(
                pond_id=request.form['pond_id'],
                species=request.form['species'],
                count=int(request.form['count']),
                average_weight=float(request.form['average_weight']),
                water_temperature=float(request.form.get('water_temperature', 25)),
                ph_level=float(request.form.get('ph_level', 7.0)),
                dissolved_oxygen=float(request.form.get('dissolved_oxygen', 6.0))
            )
            
            db.session.add(fish)
            db.session.commit()
            
            flash('Fish pond added successfully!', 'success')
            return redirect(url_for('fish.index'))
            
        except Exception as e:
            flash(f'Error adding fish pond: {str(e)}', 'error')
    
    return render_template('fish/add.html')

@fish_bp.route('/biosecurity')
def biosecurity():
    # Simulate biosecurity analysis
    risk_factors = [
        {'factor': 'Water Quality', 'status': 'Good', 'score': 85},
        {'factor': 'Disease Outbreak Risk', 'status': 'Low', 'score': 92},
        {'factor': 'Feed Quality', 'status': 'Excellent', 'score': 95},
        {'factor': 'Temperature Stability', 'status': 'Good', 'score': 88}
    ]
    
    return render_template('fish/biosecurity.html', risk_factors=risk_factors)

@fish_bp.route('/market-readiness/<int:pond_id>')
def market_readiness(pond_id):
    from app import Fish
    
    pond = Fish.query.get_or_404(pond_id)
    
    # Calculate market readiness
    readiness_score = calculate_market_readiness(pond)
    
    return render_template('fish/market_readiness.html', 
                         pond=pond, 
                         readiness=readiness_score)

@fish_bp.route('/size-estimation', methods=['GET', 'POST'])
def size_estimation():
    if request.method == 'POST':
        if 'pond_image' in request.files:
            file = request.files['pond_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'fish', filename)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                # Get form data
                pond_id = request.form.get('pond_id', '')
                species = request.form.get('species', '')
                calibration_object = request.form.get('calibration_object', 'none')
                
                # Process image and estimate fish sizes
                estimation = process_fish_image(filepath, species, calibration_object)
                
                return render_template('fish/size_result.html', 
                                     estimation=estimation,
                                     image_path=f'uploads/fish/{filename}')
    
    return render_template('fish/size_estimation.html')

def calculate_market_readiness(pond):
    """Calculate market readiness score"""
    
    # Base score
    score = 0
    factors = []
    
    # Weight factor
    if pond.average_weight >= 0.5:
        weight_score = min(100, (pond.average_weight / 1.0) * 100)
        score += weight_score * 0.4
        factors.append({'name': 'Fish Size', 'score': weight_score, 'status': 'Ready' if weight_score >= 80 else 'Growing'})
    
    # Age factor (simulated)
    age_months = random.randint(4, 12)
    age_score = min(100, (age_months / 8) * 100)
    score += age_score * 0.3
    factors.append({'name': 'Age', 'score': age_score, 'value': f'{age_months} months'})
    
    # Water quality
    water_score = 90  # Simulated
    score += water_score * 0.2
    factors.append({'name': 'Water Quality', 'score': water_score, 'status': 'Excellent'})
    
    # Market demand (simulated)
    demand_score = random.randint(75, 95)
    score += demand_score * 0.1
    factors.append({'name': 'Market Demand', 'score': demand_score, 'status': 'High'})
    
    return {
        'overall_score': round(score),
        'readiness_level': 'Ready for Market' if score >= 80 else 'Needs More Time',
        'estimated_days': max(0, random.randint(0, 30)) if score < 80 else 0,
        'factors': factors,
        'estimated_price': round(pond.average_weight * pond.count * 150, 2)  # ₹150 per kg
    }

def simulate_size_estimation():
    """Simulate AI fish size estimation"""
    
    # Generate mock data
    fish_detected = random.randint(15, 50)
    
    sizes = []
    for i in range(fish_detected):
        length = random.uniform(12, 25)  # cm
        estimated_weight = (length ** 3) * 0.00001  # Simple weight estimation
        sizes.append({
            'fish_id': i + 1,
            'length_cm': round(length, 1),
            'estimated_weight_g': round(estimated_weight * 1000, 0)
        })
    
    avg_length = sum([f['length_cm'] for f in sizes]) / len(sizes)
    avg_weight = sum([f['estimated_weight_g'] for f in sizes]) / len(sizes)
    
    return {
        'fish_detected': fish_detected,
        'individual_measurements': sizes[:10],  # Show first 10
        'average_length': round(avg_length, 1),
        'average_weight': round(avg_weight, 0),
        'size_distribution': {
            'small': len([f for f in sizes if f['length_cm'] < 15]),
            'medium': len([f for f in sizes if 15 <= f['length_cm'] < 20]),
            'large': len([f for f in sizes if f['length_cm'] >= 20])
        },
        'market_ready_percentage': round(len([f for f in sizes if f['length_cm'] >= 18]) / len(sizes) * 100, 1)
    }
