from flask import Flask

# inicializa o Flask
app = Flask(__name__)

# Definição das rotas
@app.route('/')
def helloWorld():
    return 'Hello World' 

# Executando o app com o método de depuração ativado
if __name__ == '__main__':
    app.run(debug=True)