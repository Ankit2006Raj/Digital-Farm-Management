from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta, date
import random
import json
from . import db

calendar_bp = Blueprint('calendar', __name__, template_folder='../templates/calendar')

# Define Calendar models if needed
class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # vaccination, feeding, health-check, breeding, harvest, other
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100))  # animal IDs or location
    notes = db.Column(db.Text)
    is_ai_generated = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

@calendar_bp.route('/')
def index():
    # Get current month's events
    today = date.today()
    current_month_start = date(today.year, today.month, 1)
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)
    
    events = CalendarEvent.query.filter(
        CalendarEvent.event_date >= current_month_start,
        CalendarEvent.event_date < next_month
    ).order_by(CalendarEvent.event_date).all()
    
    # Format events for calendar display
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'type': event.event_type,
            'date': event.event_date.strftime('%Y-%m-%d'),
            'time': event.event_time.strftime('%H:%M'),
            'location': event.location,
            'notes': event.notes,
            'is_ai_generated': event.is_ai_generated,
            'is_completed': event.is_completed,
            'day': event.event_date.day
        })
    
    # Get upcoming events (next 7 days)
    upcoming_end = today + timedelta(days=7)
    upcoming_events = CalendarEvent.query.filter(
        CalendarEvent.event_date >= today,
        CalendarEvent.event_date <= upcoming_end
    ).order_by(CalendarEvent.event_date).all()
    
    # Format upcoming events
    upcoming = []
    for event in upcoming_events:
        upcoming.append({
            'id': event.id,
            'title': event.title,
            'type': event.event_type,
            'date': event.event_date.strftime('%Y-%m-%d'),
            'time': event.event_time.strftime('%H:%M'),
            'location': event.location,
            'notes': event.notes,
            'is_completed': event.is_completed
        })
    
    # Get current month name for display
    current_month = today.strftime('%B %Y')
    
    return render_template('calendar/index.html', events=calendar_events, upcoming=upcoming, today=today, current_month=current_month)

@calendar_bp.route('/add', methods=['POST'])
def add_event():
    # Get form data
    data = request.form
    
    # Parse date and time
    event_date = datetime.strptime(data.get('event_date'), '%Y-%m-%d').date()
    event_time = datetime.strptime(data.get('event_time'), '%H:%M').time()
    
    # Create new event
    new_event = CalendarEvent(
        title=data.get('title'),
        event_type=data.get('event_type'),
        event_date=event_date,
        event_time=event_time,
        location=data.get('location'),
        notes=data.get('notes'),
        is_ai_generated=False
    )
    
    # Add to database
    db.session.add(new_event)
    db.session.commit()
    
    flash('Event added successfully!', 'success')
    return redirect(url_for('calendar.index'))

@calendar_bp.route('/toggle_complete/<int:event_id>', methods=['POST'])
def toggle_complete(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    event.is_completed = not event.is_completed
    db.session.commit()
    return jsonify({'success': True, 'is_completed': event.is_completed})

@calendar_bp.route('/complete/<int:event_id>', methods=['POST'])
def complete_event(event_id):
    # Get event
    event = CalendarEvent.query.get_or_404(event_id)
    
    # Mark as completed
    event.is_completed = True
    db.session.commit()
    
    return jsonify({'success': True})

@calendar_bp.route('/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    # Get event
    event = CalendarEvent.query.get_or_404(event_id)
    
    # Delete event
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('calendar.index'))

@calendar_bp.route('/generate-ai-schedule', methods=['POST'])
def generate_ai_schedule():
    try:
        # Get all animals
        from app import Cattle, Fish, Poultry
        
        cattle = Cattle.query.all()
        fish = Fish.query.all()
        poultry = Poultry.query.all()
        
        # Generate AI schedule
        new_events = []
        
        # Generate cattle events
        for cow in cattle:
            # Vaccination event
            vac_date = date.today() + timedelta(days=random.randint(1, 30))
            vac_time = datetime.strptime(f"{random.randint(8, 17)}:00", "%H:%M").time()
            
            vac_event = CalendarEvent(
                title=f"Vaccination for {cow.tag_number}",
                event_type="vaccination",
                event_date=vac_date,
                event_time=vac_time,
                location=f"Cattle {cow.tag_number}",
                notes=f"Regular vaccination for {cow.breed} cattle",
                is_ai_generated=True
            )
            
            new_events.append(vac_event)
            
            # Health check event
            health_date = date.today() + timedelta(days=random.randint(1, 14))
            health_time = datetime.strptime(f"{random.randint(8, 17)}:00", "%H:%M").time()
            
            health_event = CalendarEvent(
                title=f"Health check for {cow.tag_number}",
                event_type="health-check",
                event_date=health_date,
                event_time=health_time,
                location=f"Cattle {cow.tag_number}",
                notes=f"Regular health check for {cow.breed} cattle",
                is_ai_generated=True
            )
            
            new_events.append(health_event)
        
        # Generate fish events
        for pond in fish:
            # Water quality check
            water_date = date.today() + timedelta(days=random.randint(1, 7))
            water_time = datetime.strptime(f"{random.randint(8, 17)}:00", "%H:%M").time()
            
            water_event = CalendarEvent(
                title=f"Water quality check for {pond.pond_id}",
                event_type="health-check",
                event_date=water_date,
                event_time=water_time,
                location=f"Fish pond {pond.pond_id}",
                notes=f"Check pH, temperature, and oxygen levels",
                is_ai_generated=True
            )
            
            new_events.append(water_event)
            
            # Feeding schedule
            feed_date = date.today() + timedelta(days=random.randint(1, 3))
            feed_time = datetime.strptime(f"{random.randint(8, 17)}:00", "%H:%M").time()
            
            feed_event = CalendarEvent(
                title=f"Feeding for {pond.pond_id}",
                event_type="feeding",
                event_date=feed_date,
                event_time=feed_time,
                location=f"Fish pond {pond.pond_id}",
                notes=f"Regular feeding for {pond.species}",
                is_ai_generated=True
            )
            
            new_events.append(feed_event)
        
        # Generate poultry events
        for coop in poultry:
            # Egg collection
            egg_date = date.today() + timedelta(days=random.randint(1, 2))
            egg_time = datetime.strptime(f"{random.randint(6, 10)}:00", "%H:%M").time()
            
            egg_event = CalendarEvent(
                title=f"Egg collection for {coop.coop_id}",
                event_type="harvest",
                event_date=egg_date,
                event_time=egg_time,
                location=f"Poultry coop {coop.coop_id}",
                notes=f"Daily egg collection",
                is_ai_generated=True
            )
            
            new_events.append(egg_event)
            
            # Vaccination
            vac_date = date.today() + timedelta(days=random.randint(14, 30))
            vac_time = datetime.strptime(f"{random.randint(8, 17)}:00", "%H:%M").time()
            
            vac_event = CalendarEvent(
                title=f"Vaccination for {coop.coop_id}",
                event_type="vaccination",
                event_date=vac_date,
                event_time=vac_time,
                location=f"Poultry coop {coop.coop_id}",
                notes=f"Regular vaccination for {coop.breed}",
                is_ai_generated=True
            )
            
            new_events.append(vac_event)
        
        # Add all events to database
        for event in new_events:
            db.session.add(event)
        
        db.session.commit()
        
        flash(f'AI generated {len(new_events)} events for your farm calendar!', 'success')
        return redirect(url_for('calendar.index'))
        
    except Exception as e:
        flash(f'Error generating AI schedule: {str(e)}', 'danger')
        return redirect(url_for('calendar.index'))
