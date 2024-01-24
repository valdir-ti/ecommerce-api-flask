from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# inicializa o Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

# Modelagem dos dados
# Produto(id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

# Definição das rotas
@app.route('/')
def helloWorld():
    return 'App is running!' 

@app.route('/api/products/add', methods=['POST'])
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data['name'],price=data['price'],description=data.get('description', ''))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Produto added successfully'})
    
    return jsonify({'message': 'Invalid product data'}), 400

# Executando o app com o método de depuração ativado
if __name__ == '__main__':
    app.run(debug=True)