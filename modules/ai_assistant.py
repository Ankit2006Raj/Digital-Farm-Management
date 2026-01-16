from flask import Blueprint, render_template

assistant_bp = Blueprint('ai_assistant', __name__, template_folder='../templates/assistant')

@assistant_bp.route('/')
def index():
    return render_template('assistant/index.html')
