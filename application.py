from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# inicializa o Flask
application = Flask(__name__)
application.config['SECRET_KEY'] = 'minha_secret_key'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(application)
login_manager.init_app(application)
login_manager.login_view = 'login'
CORS(application)

# Modelagem dos dados
# User(id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)
    cart = db.relationship('CartItem', backref='user', lazy=True)

# Produto(id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

# CartItem(id, user_id, product_id)
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# Autenticação
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Definição das rotas
@application.route('/')
def helloWorld():
    return jsonify({'message': 'App is running!'})

# Login
@application.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()

    if user and data.get('password') == user.password:
            login_user(user)
            return jsonify({'message': 'Logged in successfully'})
    return jsonify({'message': 'Unauthorized. Invalid credentials'}), 401

# Loout
@application.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

# Add Product
@application.route('/api/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data['name'],price=data['price'],description=data.get('description', ''))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Produto added successfully'}), 201

    return jsonify({'message': 'Invalid product data'}), 400

# Delete Product
@application.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})

    return jsonify({'message': 'Product not found'}), 404

# Get Product details
@application.route('/api/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        })

    return jsonify({'message': 'Product not found'}), 404

# Update Product
@application.route('/api/products/update/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    data = request.json
    if 'name' in data:
        product.name = data['name']

    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']

    db.session.commit()

    return jsonify({'message': 'Product updated successfully'})

# Get Products List
@application.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
        }
        product_list.append(product_data)

    return jsonify(product_list)

# CART Endpoints
@application.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # Usuário
    user = User.query.get(int(current_user.id))
    # Produto
    product = Product.query.get(product_id)

    if user and product:
        cartItem = CartItem(user_id=user.id,product_id=product.id)
        db.session.add(cartItem)
        db.session.commit()
        return jsonify({'message': 'Item added to the cart successfully'})
    return jsonify({'message': 'Failed to add item to the cart'}), 400

@application.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@login_required
def remove_item_from_cart(item_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id,product_id=item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({ 'message': 'Item removed successfully' })
    return jsonify({ 'message': 'Item not found' }), 400

@application.route('/api/cart', methods=['GET'])
@login_required
def cart_list():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_list = []
    if cart_items:
        for cart_item in cart_items:
            product = Product.query.get(cart_item.product_id)
            cart_item = {
                'id': cart_item.id,
                'user_id': cart_item.user_id,
                'product_id': cart_item.product_id,
                'product_name': product.name,
                'product_price': product.price
            }
            cart_list.append(cart_item)
        return jsonify(cart_list)
    return jsonify({ 'message': 'Cart not found' }), 400

@application.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Checkout successfully'})


# Executando o app com o método de depuração ativado
if __name__ == '__main__':
    application.run(debug=True)