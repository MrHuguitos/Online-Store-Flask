from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_paginate import Pagination
from datetime import date
import os
import datetime
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
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    dados_carrinho = []
    total = 0

    db.execute("SELECT produtos.nome, produtos.cod, produtos.imagem, produtos.valor, carrinho.quantidade, promocao.desconto FROM produtos JOIN carrinho ON carrinho.cod_produtos = produtos.cod LEFT JOIN promocao ON promocao.cod_produtos = produtos.cod WHERE carrinho.email_cliente = %s;", (user_id,))

    for linha in db.fetchall():
        nome_produto = linha[0]
        cod_produto = linha[1]
        imagem_produto = base64.b64encode(linha[2]).decode('utf-8')
        valor_produto = str("{:.2f}".format(linha[3] * (1 - linha[5]))).replace(
            '.', ',') if linha[5] else str(linha[3]).replace('.', ',')
        quant_produto = linha[4]
        total += ((linha[3] * (1 - linha[5])) * linha[4]
                  ) if linha[5] else (linha[3] * linha[4])

        produtos = {"nome": nome_produto,
                    "codigo": cod_produto,
                    "foto": imagem_produto,
                    "valor": valor_produto,
                    "quantidade": quant_produto}

        dados_carrinho.append(produtos)
    mensagem = request.args.get('mensagem', '')

    return render_template("carrinho.html", products=dados_carrinho, total=str(total).replace('.', ','), mensagem=mensagem)


# Atualizar quantidade de produtos no carrinho
@app.route('/update-quantity', methods=['POST'])
def update_quantity():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    data = request.get_json()
    product_id = data['product_id']
    new_quantity = data['quantity']

    db.execute("UPDATE carrinho SET quantidade = %s WHERE email_cliente = %s AND cod_produtos = %s;",
               (new_quantity, user_id, product_id))
    banco.commit()

    return jsonify({'success': True, 'new_quantity': new_quantity}), 200


@app.route('/comprar', methods=['POST'])  # Realizar compra
def comprar():
    cpf = corrigir.corrigir_input(request.form['cpf'])
    senha = request.form['senha']
    user_id = session['user_id']
    codigos = request.form.getlist('codigos')

    hoje = datetime.date.today()

    db.execute(
        "SELECT senha FROM cliente WHERE email = %s AND cpf = %s;", (user_id, cpf))
    linha = db.fetchone()

    if linha and check_password_hash(linha[0], senha):
        for i in codigos:
            db.execute("SELECT produtos.valor, carrinho.quantidade, produtos.quantidade, promocao.desconto FROM produtos JOIN carrinho ON carrinho.cod_produtos = produtos.cod LEFT JOIN promocao ON promocao.cod_produtos = produtos.cod WHERE carrinho.cod_produtos = %s AND carrinho.email_cliente = %s;", (i, user_id))
            linha = db.fetchone()

            valor_total = float("{:.2f}".format(
                linha[0] * (1 - linha[3]))) * linha[1] if linha[3] else linha[0] * linha[1]
            estoque = linha[2] - linha[1]

            db.execute(
                "INSERT INTO compra(email_cliente, cod_produtos, valor, data) VALUES (%s, %s, %s, %s);", (user_id, i, valor_total, hoje))
            db.execute(
                "DELETE FROM carrinho WHERE cod_produtos = %s AND email_cliente = %s;", (i, user_id))
            db.execute(
                "UPDATE produtos SET quantidade = %s WHERE cod = %s;", (estoque, i))
            banco.commit()

        return redirect(url_for('home', mensagem="Compra realizada com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem="Dados incorretos! Tente novamente mais tarde."))


@app.route('/comprados', methods=['GET'])   # Verificar compras feitas
def comprados():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    db.execute("SELECT produtos.nome, compra.cod_compra, produtos.imagem, compra.valor, compra.data, avaliacao.nota FROM produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra WHERE compra.email_cliente = %s ORDER BY compra.cod_compra DESC;", (user_id,))

    resultados = db.fetchall()

    dados_compra = []

    for linha in resultados:
        nome_produto = linha[0]
        cod_compra = linha[1]
        imagem_produto = base64.b64encode(linha[2]).decode('utf-8')
        valor_compra = str(linha[3]).replace('.', ',')
        data_compra = corrigir_data(linha[4])
        avaliacao = linha[5] if linha[5] else None

        produtos = {"nome": nome_produto,
                    "codigo_compra": cod_compra,
                    "foto": imagem_produto,
                    "valor": valor_compra,
                    "data": data_compra,
                    "avaliacao": avaliacao}

        dados_compra.append(produtos)

    return render_template("compras.html", products=dados_compra)


@app.route('/avaliar/<cod>', methods=['POST'])   # Verificar compras feitas
def avaliar(cod):
    texto = request.form['avalie']
    estrela = request.form['estrela']

    if estrela:
        db.execute(
            "INSERT INTO avaliacao VALUES (%s, %s, %s);", (cod, estrela, texto))
        banco.commit()
        return redirect(url_for('home', mensagem="Compra avaliada com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem="Avaliação inválida!"))


@app.route('/reavaliar/<cod>', methods=['POST'])   # Verificar compras feitas
def reavaliar(cod):
    texto = request.form['avalie']
    estrela = request.form['estrela']

    if estrela:
        db.execute(
            "UPDATE avaliacao SET nota = %s, descricao = %s WHERE compra_cod = %s;", (estrela, texto, cod))
        banco.commit()
        return redirect(url_for('home', mensagem="Compra avaliada com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem="Avaliação inválida!"))


if __name__ == "__main__":
    app.run(debug=True)