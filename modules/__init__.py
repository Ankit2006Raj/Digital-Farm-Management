# Modules package initialization
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy instance that can be imported by all modules
db = SQLAlchemy()

# Create a function to initialize the app with the database
def init_app(app):
    # Initialize the SQLAlchemy app
    db.init_app(app)
    
    # Import and register blueprints
    from .cattle import cattle_bp
    from .fish import fish_bp
    from .poultry import poultry_bp
    from .ai_analytics import ai_bp
    from .community import community_bp
    from .marketplace import marketplace_bp
    from .calendar_module import calendar_bp
    from .ai_assistant import assistant_bp
    
    # Register blueprints
    app.register_blueprint(cattle_bp, url_prefix='/cattle')
    app.register_blueprint(fish_bp, url_prefix='/fish')
    app.register_blueprint(poultry_bp, url_prefix='/poultry')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    app.register_blueprint(assistant_bp, url_prefix='/assistant')
    
    return app