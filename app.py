from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta, time
import os
from modules import db, init_app
from modules.cattle import Cattle
from modules.fish import Fish
from modules.poultry import Poultry
from modules.calendar_module import CalendarEvent
from modules.marketplace import MarketplaceItem
from modules.ai_analytics import AIAnalysis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize the app with the shared SQLAlchemy instance
init_app(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/cattle', exist_ok=True)
os.makedirs('static/uploads/fish', exist_ok=True)
os.makedirs('static/uploads/poultry', exist_ok=True)

# Database Models
class Farm(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.String(100))
    location = db.Column(db.String(200))
    size = db.Column(db.Float)
    established_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class HealthRecord(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    animal_type = db.Column(db.String(50), nullable=False)  # cattle, fish, poultry
    animal_id = db.Column(db.String(50), nullable=False)  # tag_number, pond_id, coop_id
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    condition = db.Column(db.String(100))
    treatment = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

# Function to create database tables
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Add sample data if tables are empty
        if Farm.query.count() == 0:
            # Add sample farm
            farm = Farm(name="Green Acres Farm", location="123 Country Road", size=150, established_date=datetime(2010, 5, 15))
            db.session.add(farm)
            
            # Add sample cattle
            cattle1 = Cattle(tag_number="C001", breed="Angus", date_of_birth=datetime(2020, 3, 15).date(), gender="Female", weight=550)
            cattle2 = Cattle(tag_number="C002", breed="Hereford", date_of_birth=datetime(2019, 6, 10).date(), gender="Male", weight=650)
            cattle3 = Cattle(tag_number="C003", breed="Holstein", date_of_birth=datetime(2021, 1, 5).date(), gender="Female", weight=450)
            db.session.add_all([cattle1, cattle2, cattle3])
            
            # Add sample fish
            fish1 = Fish(pond_id="P001", species="Tilapia", count=500, stocking_date=datetime(2022, 4, 10).date(), water_temperature=24.5, ph_level=7.2)
            fish2 = Fish(pond_id="P002", species="Catfish", count=300, stocking_date=datetime(2022, 3, 5).date(), water_temperature=23.8, ph_level=7.0)
            db.session.add_all([fish1, fish2])
            
            # Add sample poultry
            poultry1 = Poultry(coop_id="CP001", breed="Rhode Island Red", count=50, egg_production_daily=40)
            poultry2 = Poultry(coop_id="CP002", breed="Pekin", count=25, egg_production_daily=20)
            db.session.add_all([poultry1, poultry2])
            
            # Add sample health records
            health1 = HealthRecord(animal_type="Cattle", animal_id="C001", condition="Routine Checkup", treatment="Vaccination", notes="Annual vaccination complete")
            health2 = HealthRecord(animal_type="Fish", animal_id="North Pond", condition="Water Quality Issue", treatment="Water Change", notes="Adjusted pH levels")
            db.session.add_all([health1, health2])
            
            # Add sample calendar events
            today = datetime.today().date()
            event1 = CalendarEvent(title="Cattle Vaccination", event_type="vaccination", event_date=today + timedelta(days=2), event_time=time(9, 0), location="Barn 1", notes="Schedule vaccination for all cattle", is_completed=False)
            event2 = CalendarEvent(title="Fish Pond Cleaning", event_type="maintenance", event_date=today + timedelta(days=5), event_time=time(10, 30), location="Pond P001", notes="Clean and maintain fish ponds", is_completed=False)
            event3 = CalendarEvent(title="Feed Delivery", event_type="feeding", event_date=today + timedelta(days=1), event_time=time(8, 0), location="Storage", notes="Scheduled delivery of feed supplies", is_completed=False)
            db.session.add_all([event1, event2, event3])
            
            # Add sample marketplace items
            item1 = MarketplaceItem(title="Organic Eggs", description="Farm fresh organic eggs", price=4.99, category="Products", seller_name="Green Acres Farm", contact_info="555-123-4567")
            item2 = MarketplaceItem(title="Hay Bales", description="Fresh hay bales for livestock", price=8.50, category="Supplies", seller_name="Green Acres Farm", contact_info="555-123-4567")
            item3 = MarketplaceItem(title="Tractor Rental", description="Daily rental of farm tractor", price=75.00, category="Services", seller_name="Green Acres Farm", contact_info="555-123-4567")
            db.session.add_all([item1, item2, item3])
            
            # Add sample AI analysis
            analysis1 = AIAnalysis(analysis_type="health", entity_type="cattle", entity_id="C001", prediction="Predicted 15% increase in cattle health with new feed regimen", confidence=0.85, created_date=datetime.utcnow())
            analysis2 = AIAnalysis(analysis_type="production", entity_type="fish", entity_id="P001", prediction="Predicted 20% increase in fish yield with water quality improvements", confidence=0.78, created_date=datetime.utcnow())
            db.session.add_all([analysis1, analysis2])
            
            db.session.commit()

# Dashboard route
@app.route('/')
def dashboard():
    # Get counts from each module
    cattle_count = Cattle.query.count()
    fish_count = Fish.query.count()
    poultry_count = Poultry.query.count()
    
    # Calculate total animals
    total_animals = cattle_count
    
    # Add fish count (if available)
    fish_total = sum([f.count for f in Fish.query.all() if f.count]) if fish_count > 0 else 0
    total_animals += fish_total
    
    # Add poultry count (if available)
    poultry_total = sum([p.count for p in Poultry.query.all() if p.count]) if poultry_count > 0 else 0
    total_animals += poultry_total
    
    # Get recent health records
    recent_health = HealthRecord.query.order_by(HealthRecord.record_date.desc()).limit(5).all()
    
    # Get upcoming calendar events
    today = datetime.today().date()
    upcoming_end = today + timedelta(days=7)
    upcoming_events = CalendarEvent.query.filter(
        CalendarEvent.event_date >= today,
        CalendarEvent.event_date <= upcoming_end
    ).order_by(CalendarEvent.event_date).limit(5).all()
    
    # Get AI analytics insights
    recent_analytics = AIAnalysis.query.order_by(AIAnalysis.created_date.desc()).limit(3).all()
    
    # Add missing variables that are used in the dashboard template
    total_revenue = 25000  # Example value, replace with actual calculation if available
    active_animals = total_animals  # Using total_animals as active_animals
    health_score = 85.5  # Example value, replace with actual calculation if available
    farm_info = Farm.query.first()  # Get farm information for the dashboard
    marketplace_items = MarketplaceItem.query.limit(3).all()  # Recent marketplace items
    
    return render_template('dashboard.html',
                         cattle_count=cattle_count,
                         fish_count=fish_count,
                         poultry_count=poultry_count,
                         total_animals=total_animals,
                         recent_health=recent_health,
                         upcoming_events=upcoming_events,
                         total_revenue=total_revenue,
                         active_animals=active_animals,
                         health_score=health_score,
                         farm_info=farm_info,
                         marketplace_items=marketplace_items,
                         recent_analytics=recent_analytics)

# Create database tables and run the app
if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
