from flask import Blueprint, render_template

community_bp = Blueprint('community', __name__, template_folder='../templates/community')

@community_bp.route('/')
def index():
    return render_template('community/index.html')
