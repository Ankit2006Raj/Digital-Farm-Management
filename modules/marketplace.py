from flask import Blueprint, render_template, request, jsonify
from . import db

marketplace_bp = Blueprint('marketplace', __name__, template_folder='../templates/marketplace')

# Define Marketplace model
class MarketplaceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # cattle, fish, poultry, equipment, feed, etc.
    seller_name = db.Column(db.String(100))
    contact_info = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_available = db.Column(db.Boolean, default=True)

@marketplace_bp.route('/')
def index():
    # Get marketplace items
    items = MarketplaceItem.query.filter_by(is_available=True).order_by(MarketplaceItem.date_posted.desc()).all()
    
    # Format items for display
    marketplace_items = []
    for item in items:
        marketplace_items.append({
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'price': item.price,
            'category': item.category,
            'seller_name': item.seller_name,
            'contact_info': item.contact_info,
            'date_posted': item.date_posted.strftime('%Y-%m-%d'),
            'is_available': item.is_available
        })
    
    return render_template('marketplace/index.html', items=marketplace_items)

@marketplace_bp.route('/add', methods=['POST'])
def add_item():
    # Get form data
    data = request.form
    
    # Create new marketplace item
    new_item = MarketplaceItem(
        title=data.get('title'),
        description=data.get('description'),
        price=float(data.get('price')),
        category=data.get('category'),
        seller_name=data.get('seller_name'),
        contact_info=data.get('contact_info')
    )
    
    # Add to database
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Item added successfully'})

@marketplace_bp.route('/item/<int:item_id>')
def view_item(item_id):
    # Get item details
    item = MarketplaceItem.query.get_or_404(item_id)
    
    # Format item for display
    item_data = {
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'price': item.price,
        'category': item.category,
        'seller_name': item.seller_name,
        'contact_info': item.contact_info,
        'date_posted': item.date_posted.strftime('%Y-%m-%d'),
        'is_available': item.is_available
    }
    
    return render_template('marketplace/item.html', item=item_data)
