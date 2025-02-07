from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_paginate import Pagination
import os
import src.models.models as models
import src.dbconfig.dbconfig as db
import src.etc.corrigir as corrigir
import src.controller.controller as controller

PER_PAGE = 8  # Quantidade de itens por página

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'defaultsecret')


@app.route('/home')  # Página Principal
def home():
    page = request.args.get('page', 1, type=int)  # Página atual, que por padrão será a primeira página
    offset = (page - 1) * PER_PAGE  # Obtém os itens da página atual
    
    produtos_lista = models.produtos_listagem(PER_PAGE, offset, False)  # Obter todos os produtos, com suas devidas informações
    produtos_quant = models.quant_produtos(False) # Obter a quantidade de produtos diferentes cadastrados

    pagination = Pagination(page=page, per_page=PER_PAGE, total=produtos_quant, css_framework='bootstrap3')  # Configuração da paginação
    mensagem = request.args.get('mensagem', '')  # Extrai a mensagem da URL e a passa para o template home.html

    if 'user_id' not in session:
        return render_template("principal.html", products=produtos_lista, pagination=pagination, promo=False, mensagem=mensagem)

    user = models.user_verification(session['user_id'])

    return render_template("principal.html", products=produtos_lista, pagination=pagination, user=user[0], promo=False, mensagem=mensagem)


@app.route('/home/<tipo>', methods=['GET']) # Página com os produtos de cada categoria
def home_product(tipo):
    page = request.args.get('page', 1, type=int) # Página atual (por padrão, será a primeira página)
    offset = (page - 1) * PER_PAGE  # Obtém os itens da página atual

    produtos_lista = models.produtos_listagem(PER_PAGE, offset, tipo)  # Obter todos os produtos, com suas devidas informações
    produtos_quant = models.quant_produtos(tipo)  # Obter a quantidade de produtos diferentes cadastrados

    pagination = Pagination(page=page, per_page=PER_PAGE, total=produtos_quant, css_framework='bootstrap3')  # Configuração da paginação

    if 'user_id' not in session:
        return render_template("principal.html", products=produtos_lista, pagination=pagination, promo=False)

    user = models.user_verification(session['user_id'])

    return render_template("principal.html", products=produtos_lista, pagination=pagination, user=user[0], promo=False)


@app.route('/promocoes', methods=['GET'])   # Página com as promoções
def promocoes():
    page = request.args.get('page', 1, type=int)  # Página atual (por padrão, será a primeira página)
    offset = (page - 1) * PER_PAGE  # Obtém os itens da página atual
    
    produtos_lista = models.produtos_promocao(PER_PAGE, offset)  # Obter todos os produtos, com suas devidas informações
    produtos_quant = models.quant_prod_promocao()  # Obter a quantidade de produtos diferentes cadastrados

    pagination = Pagination(page=page, per_page=PER_PAGE, total=produtos_quant, css_framework='bootstrap3')  # Configuração da paginação

    if 'user_id' not in session:
        return render_template("principal.html", products=produtos_lista, pagination=pagination, promo=True)

    user = models.user_verification(session['user_id'])

    return render_template("principal.html", products=produtos_lista, pagination=pagination, user=user[0], promo=True)


@app.route('/sign-up', methods=['GET', 'POST'])  # Cadastro de usuários
def cadastro():
    if request.method == 'POST':
        return controller.sigup()
    return render_template("sign-up.html")


@app.route('/log-in', methods=['GET', 'POST'])  # Login do usuário
def login():
    if request.method == 'POST':
        return controller.login()
    return render_template("log-in.html")


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
        nome = request.form['search']
        return controller.produto(nome)
    else:
        return render_template("produto.html", nome2="", valor2="", quantidade2="", categoria2="", foto2="", codigo2="")


@app.route('/save-product/<codigo>', methods=['POST'])  # Salvar o produto no carrinho
def save_product(codigo):
    if 'user_id' not in session:
        return redirect(url_for('login'))

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