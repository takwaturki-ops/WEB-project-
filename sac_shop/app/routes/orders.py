
from flask import Blueprint, jsonify, request, session
from ..database import get_db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/cart', methods=['GET'])
def get_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Non connecté'}), 401
    db = get_db()
    items = db.execute(
        '''SELECT cart.id, products.name, products.price,
           cart.quantity, products.image_url
           FROM cart JOIN products ON cart.product_id = products.id
           WHERE cart.user_id = ?''', (user_id,)
    ).fetchall()
    return jsonify([dict(i) for i in items])

@orders_bp.route('/cart', methods=['POST'])
def add_to_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Non connecté'}), 401
    data = request.get_json()
    db = get_db()
    existing = db.execute(
        'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
        (user_id, data['product_id'])
    ).fetchone()
    if existing:
        db.execute(
            'UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?',
            (user_id, data['product_id'])
        )
    else:
        db.execute(
            'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
            (user_id, data['product_id'], data.get('quantity', 1))
        )
    db.commit()
    return jsonify({'message': 'Ajouté au panier'}), 201

@orders_bp.route('/cart/<int:id>', methods=['DELETE'])
def remove_from_cart(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Non connecté'}), 401
    db = get_db()
    db.execute('DELETE FROM cart WHERE id = ? AND user_id = ?', (id, user_id))
    db.commit()
    return jsonify({'message': 'Retiré du panier'})

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Non connecté'}), 401
    db = get_db()
    cart_items = db.execute(
        '''SELECT cart.product_id, cart.quantity, products.price
           FROM cart JOIN products ON cart.product_id = products.id
           WHERE cart.user_id = ?''', (user_id,)
    ).fetchall()
    if not cart_items:
        return jsonify({'error': 'Panier vide'}), 400
    total = sum(item['quantity'] * item['price'] for item in cart_items)
    cursor = db.execute(
        'INSERT INTO orders (user_id, total) VALUES (?, ?)',
        (user_id, total)
    )
    order_id = cursor.lastrowid
    for item in cart_items:
        db.execute(
            'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
            (order_id, item['product_id'], item['quantity'], item['price'])
        )
    db.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    db.commit()
    return jsonify({'message': 'Commande passée', 'order_id': order_id}), 201

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Non connecté'}), 401
    db = get_db()
    orders = db.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    return jsonify([dict(o) for o in orders])