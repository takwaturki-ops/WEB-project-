from flask import Blueprint, jsonify, request
from ..database import get_db

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    return jsonify([dict(p) for p in products])

@products_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if product is None:
        return jsonify({'error': 'Produit introuvable'}), 404
    return jsonify(dict(product))

@products_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({'error': 'Nom et prix requis'}), 400
    db = get_db()
    db.execute(
        'INSERT INTO products (name, description, price, stock, image_url, category_id) VALUES (?, ?, ?, ?, ?, ?)',
        (data['name'], data.get('description'), data['price'],
         data.get('stock', 0), data.get('image_url'), data.get('category_id'))
    )
    db.commit()
    return jsonify({'message': 'Produit créé'}), 201

@products_bp.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if product is None:
        return jsonify({'error': 'Produit introuvable'}), 404
    db.execute(
        'UPDATE products SET name=?, description=?, price=?, stock=?, image_url=? WHERE id=?',
        (data.get('name', product['name']),
         data.get('description', product['description']),
         data.get('price', product['price']),
         data.get('stock', product['stock']),
         data.get('image_url', product['image_url']),
         id)
    )
    db.commit()
    return jsonify({'message': 'Produit mis à jour'})

@products_bp.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if product is None:
        return jsonify({'error': 'Produit introuvable'}), 404
    db.execute('DELETE FROM products WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Produit supprimé'})