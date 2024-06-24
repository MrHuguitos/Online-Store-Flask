from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_paginate import Pagination
import mysql.connector
import base64
import re
import datetime

banco = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "labhugo",
    database = "farmdigital"
)
cursor = banco.cursor()

def corrigir_input(data): #Remoção de símbolos especiais de input
    return re.sub(r'\D', '', data)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

PER_PAGE = 8

@app.route('/home') #Página Principal
def home():
    page = request.args.get('page', 1, type=int) # Página atual (por padrão, será a primeira página)
    offset = (page - 1) * PER_PAGE # Obtém os itens da página atual

    cursor.execute(f"SELECT nome, imagem, valor FROM produtos ORDER BY valor DESC LIMIT {PER_PAGE} OFFSET {offset};")
    resultados = cursor.fetchall()

    dados_produtos = []
    for linha in resultados:
        nome_produto = linha[0]
        imagem_produto = linha[1]
        valor_produto = linha[2]
        valor_produto2 = str(valor_produto).replace('.', ',')
        imagem_base64 = base64.b64encode(imagem_produto).decode('utf-8')

        produtos = {"nome": nome_produto, "foto": imagem_base64, "valor": valor_produto2}
        dados_produtos.append(produtos)

    cursor.execute("SELECT COUNT(*) FROM produtos;")
    result = cursor.fetchone()
    total_produtos = result[0] if result else 0

    pagination = Pagination(page=page, per_page=PER_PAGE, total=total_produtos, css_framework='bootstrap3') # Configuração da paginação

    if 'user_id' not in session:
        return render_template("principal.html", products=dados_produtos, pagination=pagination)
    
    cursor.execute("SELECT nome FROM cliente WHERE email = %s;", (session['user_id'],))
    resultado = cursor.fetchone()
    
    return render_template("principal2.html", products=dados_produtos, pagination=pagination, user=resultado[0])

@app.route('/sign-up', methods=['GET', 'POST']) #Cadastro de usuários
def cadastro():
    if request.method == 'POST':
        email = request.form['mail']
        cpf = corrigir_input(request.form['cpf'])
        nome = request.form['nome']
        nascimento = request.form['nascimento']
        estado = request.form['state']
        cidade = request.form['city']
        bairro = request.form['district']
        rua = request.form['street']
        numero = request.form['number']
        senha = request.form['senha']
        telefone = request.form.getlist('phone')

        cursor.execute("SELECT email, cpf FROM cliente WHERE email = %s OR cpf = %s;", (email, cpf))
        linha = cursor.fetchone()

        if linha is not None: 
            return redirect(url_for('home'))
        else:
            cursor.execute("INSERT INTO cliente VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (email, cpf, senha, nome, estado, cidade, bairro, rua, numero, nascimento))
            banco.commit()
            for i in telefone:
                i2 = corrigir_input(i)
                cursor.execute("INSERT INTO contato_cliente VALUES (%s, %s);", (i2, email))
                banco.commit()
            return redirect(url_for('home'))   
    else:
        return render_template("Sign-up.html")

@app.route('/log-in', methods=['GET', 'POST']) #Login do usuário
def login():
    if request.method == 'POST':
        email = request.form['mail']
        senha = request.form['senha']

        cursor.execute("SELECT email, senha FROM cliente WHERE email = %s AND senha = %s;", (email, senha))
        linha = cursor.fetchone()

        if linha is not None:
            session['user_id'] = linha[0] 
            return redirect(url_for('home'))
        else:
            return render_template("Log-in.html", mensagem="Parece que não existe um usuário com essas credenciais. Confira seus dados e tente novamente!")   
    else:
        return render_template("Log-in.html")

@app.route('/log-out') #Logout do usuário
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/produto/<nome>', methods=['GET']) #Produto
def mostrar_produtos(nome):
    cursor.execute("SELECT nome, valor, quantidade, categoria, imagem, cod FROM produtos WHERE nome = %s;", (nome,))

    linha = cursor.fetchone()

    nome_prod = linha[0]
    valor_prod = str(linha[1]).replace('.', ',')
    quantidade_prod = linha[2]
    categoria_prod = linha[3]
    foto_prod = base64.b64encode(linha[4]).decode('utf-8') #Converter os dados binários em uma imagem
    cod_prod = linha[5]

    return render_template("produto.html", nome2 = nome_prod, valor2 = valor_prod, quantidade2 = quantidade_prod, categoria2 = categoria_prod, foto2 = foto_prod, codigo2 = cod_prod)

@app.route('/produto', methods=['GET', 'POST']) #Produto pesquisado
def mostrar_produto_pesquisado():
    if request.method == 'POST':
        nomeproduto = request.form['search']
        cursor.execute("SELECT nome, valor, quantidade, categoria, imagem, cod FROM produtos WHERE nome = %s;", (nomeproduto,))

        linha = cursor.fetchone()

        if linha:
            nome_prod = linha[0]
            valor_prod = str(linha[1]).replace('.', ',')
            quantidade_prod = linha[2]
            categoria_prod = linha[3]
            foto_prod = base64.b64encode(linha[4]).decode('utf-8') #Converter os dados binários em uma imagem
            cod_prod = linha[5]

            return render_template("produto.html", nome2 = nome_prod, valor2 = valor_prod, quantidade2 = quantidade_prod, categoria2 = categoria_prod, foto2 = foto_prod, codigo2 = cod_prod)
        else:
            return redirect(url_for('home'))
    else:
        return render_template("produto.html", nome2 = "", valor2 = "", quantidade2 = "", categoria2 = "", foto2 = "", codigo2 = "")

@app.route('/save-product/<codigo>', methods=['POST']) #Salvar o produto no carrinho
def save_product(codigo):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    quantidade = request.form['quant']

    cursor.execute("INSERT INTO carrinho (cod_produtos, email_cliente, quantidade) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantidade = quantidade + VALUES(quantidade);", (codigo, user_id, quantidade))
    banco.commit()

    return redirect(url_for('home'))

@app.route('/carrinho', methods=['GET']) #Verificar carrinho
def carrinho():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    cursor.execute("SELECT produtos.nome, produtos.cod, produtos.imagem, produtos.valor, carrinho.quantidade FROM produtos, carrinho WHERE carrinho.cod_produtos = produtos.cod AND carrinho.email_cliente = %s;", (user_id,))
    resultados = cursor.fetchall()

    dados_carrinho = []
    total = 0

    for linha in resultados:
        nome_produto = linha[0]
        cod_produto = linha[1]
        imagem_produto = base64.b64encode(linha[2]).decode('utf-8')
        valor_produto = str(linha[3]).replace('.', ',')
        quant_produto = linha[4]
        total += (linha[3] * linha[4])

        produtos = {"nome": nome_produto, "codigo": cod_produto, "foto": imagem_produto, "valor": valor_produto, "quantidade": quant_produto}
        dados_carrinho.append(produtos)

    return render_template("Carrinho.html", products=dados_carrinho, total=str(total).replace('.', ','))

@app.route('/update-quantity', methods=['POST']) #Atualizar quantidade de produtos no carrinho
def update_quantity():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    data = request.get_json()
    product_id = data['product_id']
    new_quantity = data['quantity']

    cursor.execute("UPDATE carrinho SET quantidade = %s WHERE email_cliente = %s AND cod_produtos = %s;", (new_quantity, user_id, product_id))
    banco.commit()

    return jsonify({'success': True, 'new_quantity': new_quantity}), 200

@app.route('/comprar', methods=['POST']) #Realizar compra
def comprar():
    codigos = request.form.getlist('codigos')
    user_id = session['user_id']

    hoje = datetime.date.today()

    for i in codigos:
        cursor.execute("SELECT produtos.valor, carrinho.quantidade, produtos.quantidade FROM produtos, carrinho WHERE carrinho.cod_produtos = produtos.cod AND carrinho.email_cliente = %s AND produtos.cod = %s;", (user_id, i))
        linha = cursor.fetchone()

        if linha:
            valor_total = linha[0] * linha[1]
            estoque = linha[2] - linha[1]

            cursor.execute("INSERT INTO compra(email_cliente, cod_produtos, valor, data) VALUES (%s, %s, %s, %s);", (user_id, i, valor_total, hoje))
            cursor.execute("DELETE FROM carrinho WHERE cod_produtos = %s AND email_cliente = %s;", (i, user_id))
            cursor.execute("UPDATE produtos SET quantidade = %s WHERE cod = %s;", (estoque, i))
            banco.commit()

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)