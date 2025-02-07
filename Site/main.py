from flask import Flask, render_template, request, redirect, url_for, session
import os
import src.controller.controller as controller

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'defaultsecret')


@app.route('/home')  # Página Principal
def home():
    return controller.listar_produtos(False, False)


@app.route('/home/<tipo>', methods=['GET']) # Página com os produtos de cada categoria
def home_product(tipo):
    return controller.listar_produtos(tipo, False)


@app.route('/promocoes', methods=['GET'])   # Página com as promoções
def promocoes():
    return controller.listar_produtos(False, True)


@app.route('/sign-up', methods=['GET', 'POST'])  # Cadastro de usuários
def cadastro():
    return controller.sigup()


@app.route('/log-in', methods=['GET', 'POST'])  # Login do usuário
def login():
    return controller.login()


@app.route('/log-out')  # Logout do usuário
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/usuario', methods=['GET'])  # Página com os dados do usuário
def usuario():
    return controller.perfil()


@app.route('/produto/<nome>', methods=['GET'])  # Produto
def mostrar_produtos(nome):
    return controller.produto(nome)


@app.route('/produto', methods=['GET', 'POST'])  # Produto pesquisado
def mostrar_produto_pesquisado():
    if request.method == 'POST':
        return controller.produto(request.form['search'])
    else:
        return render_template("produto.html", nome2="", valor2="", quantidade2="", categoria2="", foto2="", codigo2="")


@app.route('/save-product/<codigo>', methods=['POST'])  # Salvar o produto no carrinho
def save_product(codigo):
    return controller.salvar_produtos(codigo)


@app.route('/carrinho', methods=['GET'])  # Verificar carrinho
def carrinho():
    return controller.carrinho()


@app.route('/update-quantity', methods=['POST']) # Atualizar quantidade de produtos no carrinho
def update_quantity():
    return controller.put_quantidade()


@app.route('/comprar', methods=['POST'])  # Realizar compra
def comprar():
    return controller.comprar_produto()


@app.route('/comprados', methods=['GET'])   # Verificar compras feitas
def comprados():
    return controller.historico()


@app.route('/avaliar/<cod>', methods=['POST'])   # Avaliar Produtos
def avaliar(cod):
    return controller.avaliar(cod, "avaliar")


@app.route('/reavaliar/<cod>', methods=['POST'])   # Editar avaliacao
def reavaliar(cod):
    return controller.avaliar(cod, "reavaliar")


if __name__ == "__main__":
    app.run(debug=True)