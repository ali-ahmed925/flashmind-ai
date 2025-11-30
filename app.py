import os
from flask import Flask, render_template, request, jsonify, send_file, session
from dotenv import load_dotenv
from services import PDFService, AIService, StorageService
from user_service import UserService
from auth_service import AuthService

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'flashmind-secret-key-change-in-production')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Extract text immediately to validate and prepare
        try:
            text = PDFService.extract_text(filepath)
            return jsonify({'message': 'File uploaded successfully', 'filename': file.filename, 'text_length': len(text)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/generate', methods=['POST'])
def generate_flashcards():
    data = request.json
    filename = data.get('filename')
    difficulty = data.get('difficulty', 'medium')
    amount = data.get('amount', 10)
    
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
        
    try:
        text = PDFService.extract_text(filepath)
        flashcards = AIService.generate_flashcards(text, difficulty, amount)
        StorageService.save_session(filename, flashcards)
        return jsonify({'flashcards': flashcards})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'All fields required'}), 400
    
    user, error = AuthService.register(username, email, password)
    if error:
        return jsonify({'error': error}), 400
    
    session['user_id'] = user['id']
    return jsonify(user)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password required'}), 400
    
    user, error = AuthService.login(email, password)
    if error:
        return jsonify({'error': error}), 401
    
    session['user_id'] = user['id']
    return jsonify(user)

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = AuthService.get_user(user_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    flashcards = StorageService.get_session(filename)
    return jsonify({'flashcards': flashcards})

@app.route('/api/user/deck-created', methods=['POST'])
def deck_created():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    deck_name = data.get('deck_name')
    cards_count = data.get('cards_count')
    difficulty = data.get('difficulty')
    
    user = AuthService.increment_decks_created(user_id, deck_name, cards_count, difficulty)
    if user:
        return jsonify(user)
    return jsonify({'error': 'Failed to update'}), 500

@app.route('/api/user/complete-deck', methods=['POST'])
def complete_deck():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    deck_name = data.get('deck_name')
    cards_count = data.get('cards_count')
    
    result = AuthService.complete_deck(user_id, deck_name, cards_count)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Failed to complete deck'}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get global leaderboard ranked by XP"""
    leaderboard = AuthService.get_leaderboard()
    return jsonify({'leaderboard': leaderboard})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
