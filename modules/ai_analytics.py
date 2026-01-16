from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import random
from datetime import datetime, timedelta
from . import db

ai_bp = Blueprint('ai_analytics', __name__, template_folder='../templates/ai')

# Define AI Analytics models
class AIAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_type = db.Column(db.String(50), nullable=False)  # health, production, market, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # cattle, fish, poultry
    entity_id = db.Column(db.String(50), nullable=False)  # tag_number, pond_id, coop_id
    prediction = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False)  # 0-1 confidence score
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_validated = db.Column(db.Boolean, default=False)
    validation_result = db.Column(db.Boolean, nullable=True)  # True if prediction was correct
    notes = db.Column(db.Text, nullable=True)

@ai_bp.route('/')
def index():
    # Get recent AI analyses
    recent_analyses = AIAnalysis.query.order_by(AIAnalysis.created_date.desc()).limit(10).all()
    
    # Count analyses by type
    health_analyses = AIAnalysis.query.filter_by(analysis_type='health').count()
    production_analyses = AIAnalysis.query.filter_by(analysis_type='production').count()
    market_analyses = AIAnalysis.query.filter_by(analysis_type='market').count()
    
    return render_template('ai/index.html', 
                          recent_analyses=recent_analyses,
                          health_analyses=health_analyses,
                          production_analyses=production_analyses,
                          market_analyses=market_analyses)

@ai_bp.route('/schedule-check')
def schedule_check():
    return render_template('ai/schedule_check.html')

@ai_bp.route('/health-check')
def health_check():
    return render_template('ai/health_check.html')

@ai_bp.route('/reports')
def reports():
    return render_template('ai/reports.html')

@ai_bp.route('/activity-log')
def activity_log():
    return render_template('ai/activity_log.html')

@ai_bp.route('/generate-analysis', methods=['POST'])
def generate_analysis():
    data = request.json
    analysis_type = data.get('analysis_type')
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    
    # Generate AI analysis based on type
    if analysis_type == 'health':
        prediction = "Based on recent data, this entity shows signs of optimal health with no concerning indicators."
        confidence = random.uniform(0.85, 0.98)
    elif analysis_type == 'production':
        prediction = "Production is projected to increase by 12% in the next month based on current trends."
        confidence = random.uniform(0.75, 0.92)
    elif analysis_type == 'market':
        prediction = "Market conditions suggest optimal selling time within the next 2-3 weeks."
        confidence = random.uniform(0.70, 0.88)
    else:
        prediction = "General analysis shows positive indicators across all measured metrics."
        confidence = random.uniform(0.65, 0.85)
    
    # Save analysis to database
    new_analysis = AIAnalysis(
        analysis_type=analysis_type,
        entity_type=entity_type,
        entity_id=entity_id,
        prediction=prediction,
        confidence=confidence
    )
    
    db.session.add(new_analysis)
    db.session.commit()
    
    return jsonify({
        'id': new_analysis.id,
        'prediction': prediction,
        'confidence': confidence,
        'created_date': new_analysis.created_date.strftime('%Y-%m-%d %H:%M:%S')
    })
