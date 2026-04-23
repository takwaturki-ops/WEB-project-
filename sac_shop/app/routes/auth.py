from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    db = get_db()
    hashed = generate_password_hash(data['password'])
    try:
        db.execute(
            'INSERT INTO users (email, password) VALUES (?, ?)',
            (data['email'], hashed)
        )
        db.commit()
        return jsonify({'message': 'Compte créé avec succès'}), 201
    except:
        return jsonify({'error': 'Email déjà utilisé'}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE email = ?', (data['email'],)
    ).fetchone()
    if user and check_password_hash(user['password'], data['password']):
        session['user_id'] = user['id']
        return jsonify({'message': 'Connecté', 'user_id': user['id']})
    return jsonify({'error': 'Identifiants incorrects'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Déconnecté'})