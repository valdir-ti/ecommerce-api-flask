from flask import Flask
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
    return 'Hello World' 

# Executando o app com o método de depuração ativado
if __name__ == '__main__':
    app.run(debug=True)