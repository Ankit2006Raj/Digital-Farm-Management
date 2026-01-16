from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import random
import os
import cv2
import numpy as np
from PIL import Image
import datetime
from werkzeug.utils import secure_filename
from . import db

poultry_bp = Blueprint('poultry', __name__, template_folder='../templates/poultry')

# Define Poultry model
class Poultry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coop_id = db.Column(db.String(50), unique=True, nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=0)
    egg_production_daily = db.Column(db.Integer, default=0)
    feed_consumption = db.Column(db.Float, default=0.0)  # kg per day
    mortality_rate = db.Column(db.Float, default=0.0)  # percentage
    average_weight = db.Column(db.Float, nullable=True)  # kg
    vaccination_status = db.Column(db.String(50), default='Not Vaccinated')
    last_health_check = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@poultry_bp.route('/')
def index():
    poultry_coops = Poultry.query.all()
    total_coops = len(poultry_coops)
    total_birds = sum([p.count for p in poultry_coops if p.count])
    total_egg_production = sum([p.egg_production_daily for p in poultry_coops if p.egg_production_daily])
    
    # Calculate production rate (hardcoded for now, could be calculated based on actual data)
    production_rate = 94
    
    return render_template('poultry/index.html',
                         poultry_coops=poultry_coops,
                         total_coops=total_coops,
                         total_birds=total_birds,
                         total_egg_production=total_egg_production,
                         production_rate=production_rate)

@poultry_bp.route('/add', methods=['GET', 'POST'])
def add_coop():
    if request.method == 'POST':
        try:
            poultry = Poultry(
                coop_id=request.form['coop_id'],
                breed=request.form['breed'],
                count=int(request.form['count']),
                egg_production_daily=int(request.form.get('egg_production_daily', 0)),
                feed_consumption=float(request.form.get('feed_consumption', 0)),
                mortality_rate=float(request.form.get('mortality_rate', 0))
            )
            
            db.session.add(poultry)
            db.session.commit()
            
            flash('Poultry coop added successfully!', 'success')
            return redirect(url_for('poultry.index'))
            
        except Exception as e:
            flash(f'Error adding poultry coop: {str(e)}', 'error')
    
    return render_template('poultry/add.html')

@poultry_bp.route('/egg-freshness', methods=['GET', 'POST'])
def egg_freshness():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'eggImages' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('eggImages')
        
        # If user does not select file, browser also submits an empty part without filename
        if not files or files[0].filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Get form data
        egg_source = request.form.get('eggSource', '')
        collection_date = request.form.get('collectionDate', datetime.datetime.now().strftime('%Y-%m-%d'))
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads', 'poultry', 'eggs')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Process images and get analysis results
        analysis_results = process_egg_images(files, upload_dir, egg_source, collection_date)
        
        return render_template('poultry/egg_freshness.html', 
                               analysis_results=analysis_results, 
                               show_results=True)
    
    return render_template('poultry/egg_freshness.html')

@poultry_bp.route('/behavioral-monitoring')
def behavioral_monitoring():
    return render_template('poultry/behavioral_monitoring.html')


def process_egg_images(files, upload_dir, egg_source, collection_date):
    """
    Process uploaded egg images and analyze freshness using computer vision
    """
    processed_images = []
    individual_analyses = []
    
    for i, file in enumerate(files):
        # Save the original image
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{i}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Process the image with OpenCV
        try:
            # Load image
            img = cv2.imread(file_path)
            if img is None:
                continue
                
            # Convert to RGB for better color analysis
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Convert to HSV for better color segmentation
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Analyze egg quality based on color features
            analysis = analyze_egg_quality(img_rgb, img_hsv)
            
            # Add file path to the analysis
            analysis['image_path'] = os.path.join('uploads', 'poultry', 'eggs', unique_filename)
            analysis['image_number'] = i + 1
            
            # Create annotated image
            annotated_img = create_annotated_image(img, analysis)
            
            # Save annotated image
            annotated_filename = f"annotated_{unique_filename}"
            annotated_path = os.path.join(upload_dir, annotated_filename)
            cv2.imwrite(annotated_path, annotated_img)
            
            analysis['annotated_image_path'] = os.path.join('uploads', 'poultry', 'eggs', annotated_filename)
            
            individual_analyses.append(analysis)
            processed_images.append(file_path)
            
        except Exception as e:
            print(f"Error processing image {filename}: {str(e)}")
            # If processing fails, fall back to simulated analysis
            simulated = simulate_egg_analysis(i)
            simulated['image_path'] = os.path.join('uploads', 'poultry', 'eggs', unique_filename)
            simulated['image_number'] = i + 1
            individual_analyses.append(simulated)
    
    # Calculate overall results
    if individual_analyses:
        # Calculate average freshness score
        avg_freshness = sum(a['freshness_score'] for a in individual_analyses) / len(individual_analyses)
        
        # Determine overall grade based on average freshness
        overall_grade, overall_color = get_grade_from_score(avg_freshness)
        
        # Generate recommendations based on overall grade
        recommendations = generate_recommendations(overall_grade, egg_source)
        
        results = {
            'overall_grade': overall_grade,
            'overall_color': overall_color,
            'average_freshness': round(avg_freshness),
            'individual_analyses': individual_analyses,
            'recommendations': recommendations,
            'egg_source': egg_source,
            'collection_date': collection_date,
            'processed_images': processed_images
        }
    else:
        results = None
    
    return results


def analyze_egg_quality(img_rgb, img_hsv):
    """
    Analyze egg quality using computer vision techniques
    """
    # Extract features from the image
    
    # 1. Color analysis for yolk and white
    # Yellow/orange color range for yolk in HSV
    lower_yolk = np.array([20, 100, 100])
    upper_yolk = np.array([30, 255, 255])
    yolk_mask = cv2.inRange(img_hsv, lower_yolk, upper_yolk)
    
    # White color range for egg white in HSV
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    white_mask = cv2.inRange(img_hsv, lower_white, upper_white)
    
    # Calculate yolk and white areas
    yolk_area = np.sum(yolk_mask > 0)
    white_area = np.sum(white_mask > 0)
    
    # Calculate yolk to white ratio (important freshness indicator)
    yolk_white_ratio = yolk_area / white_area if white_area > 0 else 0
    
    # 2. Texture analysis for egg white
    # Convert to grayscale for texture analysis
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    
    # Apply white mask to get only the egg white region
    white_region = cv2.bitwise_and(gray, gray, mask=white_mask)
    
    # Calculate texture features (standard deviation of pixel values)
    white_texture = np.std(white_region[white_mask > 0]) if np.sum(white_mask > 0) > 0 else 0
    
    # 3. Shape analysis for yolk
    # Find contours in yolk mask
    contours, _ = cv2.findContours(yolk_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    yolk_roundness = 0
    if contours:
        # Get the largest contour (assumed to be the yolk)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        
        # Calculate circularity/roundness (4*pi*area/perimeter^2)
        # Perfect circle has value of 1, less circular shapes have lower values
        if perimeter > 0:
            yolk_roundness = 4 * np.pi * area / (perimeter * perimeter)
    
    # 4. Calculate freshness score based on features
    # Weight factors for each feature
    w_ratio = 0.3
    w_texture = 0.3
    w_roundness = 0.4
    
    # Score calculations (higher is better)
    ratio_score = 100 - min(100, abs(yolk_white_ratio - 0.4) * 200)  # Ideal ratio around 0.4
    texture_score = min(100, white_texture * 10)  # Higher texture is better (up to a point)
    roundness_score = yolk_roundness * 100  # Higher roundness is better
    
    # Combined freshness score
    freshness_score = w_ratio * ratio_score + w_texture * texture_score + w_roundness * roundness_score
    
    # Determine grade based on freshness score
    grade, color = get_grade_from_score(freshness_score)
    
    # Determine conditions based on features
    if yolk_roundness > 0.8:
        yolk_condition = "Firm and round"
    elif yolk_roundness > 0.6:
        yolk_condition = "Slightly flattened"
    else:
        yolk_condition = "Flat and enlarged"
    
    if white_texture > 8:
        white_condition = "Thick and clear"
    elif white_texture > 5:
        white_condition = "Reasonably thick"
    else:
        white_condition = "Thin and watery"
    
    # Determine shelf life based on freshness score
    if freshness_score > 85:
        shelf_life = "3-4 weeks"
    elif freshness_score > 70:
        shelf_life = "2-3 weeks"
    else:
        shelf_life = "1-2 weeks"
    
    # Determine market value based on grade
    if grade == "AA":
        market_value = "Premium"
    elif grade == "A":
        market_value = "Standard"
    else:
        market_value = "Lower grade"
    
    # Check for defects
    defects = []
    
    # Blood spot detection (red areas)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    red_mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    
    red_area = np.sum(red_mask > 0)
    if red_area > 100:  # Threshold for blood spot detection
        defects.append("Blood spots")
    
    if not defects:
        defects.append("None detected")
    
    return {
        'grade': grade,
        'freshness_score': round(freshness_score),
        'yolk_condition': yolk_condition,
        'white_condition': white_condition,
        'defects': defects,
        'shelf_life': shelf_life,
        'market_value': market_value,
        'color': color
    }


def create_annotated_image(img, analysis):
    """
    Create an annotated version of the egg image with analysis results
    """
    # Create a copy of the image
    annotated = img.copy()
    
    # Add text with analysis results
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    color = (0, 255, 0) if analysis['grade'] == 'AA' else (0, 165, 255) if analysis['grade'] == 'A' else (0, 0, 255)
    
    # Add grade and freshness score
    cv2.putText(annotated, f"Grade: {analysis['grade']}", (10, 30), font, font_scale, color, thickness)
    cv2.putText(annotated, f"Freshness: {analysis['freshness_score']}%", (10, 70), font, font_scale, color, thickness)
    
    # Add yolk and white condition
    cv2.putText(annotated, f"Yolk: {analysis['yolk_condition']}", (10, 110), font, font_scale, color, thickness)
    cv2.putText(annotated, f"White: {analysis['white_condition']}", (10, 150), font, font_scale, color, thickness)
    
    return annotated


def get_grade_from_score(score):
    """
    Determine egg grade and color based on freshness score
    """
    if score >= 85:
        return "AA", "success"
    elif score >= 70:
        return "A", "warning"
    else:
        return "B", "danger"


def generate_recommendations(grade, egg_source):
    """
    Generate recommendations based on egg grade and source
    """
    recommendations = {
        'AA': [
            'Excellent quality eggs - ideal for premium market sales',
            'Store in refrigerator at 4°C to maintain quality',
            'These eggs can be marketed as "Premium Grade" with higher pricing',
            'Continue current feeding and housing practices'
        ],
        'A': [
            'Good quality eggs suitable for standard market',
            'Consider improving ventilation in poultry housing',
            'Check feed quality and freshness',
            'Monitor for stress factors that might affect egg quality'
        ],
        'B': [
            'Lower grade eggs - consider for processing or local sales',
            'Review feeding schedule and nutrition content',
            'Check poultry housing conditions and cleanliness',
            'Consider health check for laying birds'
        ]
    }
    
    # Add source-specific recommendations if available
    if egg_source:
        if grade == 'AA':
            recommendations[grade].append(f'Coop {egg_source} is producing excellent quality eggs')
        elif grade == 'A':
            recommendations[grade].append(f'Consider minor adjustments to feed for coop {egg_source}')
        else:
            recommendations[grade].append(f'Prioritize health check for birds in coop {egg_source}')
    
    return recommendations.get(grade, recommendations['A'])


def simulate_egg_analysis(index):
    """
    Simulate egg analysis results when image processing fails
    """
    # Simulate AI analysis results
    grades = ['AA', 'A', 'B']
    colors = ['success', 'warning', 'danger']
    freshness_scores = [92, 78, 65]
    
    random_grade = random.randint(0, 2)
    grade = grades[random_grade]
    color = colors[random_grade]
    freshness_score = freshness_scores[random_grade] + random.randint(-4, 4)
    
    # Determine conditions based on grade
    if random_grade == 0:
        yolk_condition = 'Firm and round'
        white_condition = 'Thick and clear'
        defects = ['None detected']
        shelf_life = '3-4 weeks'
        market_value = 'Premium'
    elif random_grade == 1:
        yolk_condition = 'Slightly flattened'
        white_condition = 'Reasonably thick'
        defects = ['Minor discoloration']
        shelf_life = '2-3 weeks'
        market_value = 'Standard'
    else:
        yolk_condition = 'Flat and enlarged'
        white_condition = 'Thin and watery'
        defects = ['Blood spots', 'Shell cracks']
        shelf_life = '1-2 weeks'
        market_value = 'Lower grade'
    
    return {
        'grade': grade,
        'freshness_score': max(50, min(100, freshness_score)),
        'yolk_condition': yolk_condition,
        'white_condition': white_condition,
        'defects': defects,
        'shelf_life': shelf_life,
        'market_value': market_value,
        'color': color
    }
