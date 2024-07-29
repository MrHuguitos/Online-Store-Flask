from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_paginate import Pagination
import mysql.connector
import base64
import re
import datetime
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

banco = mysql.connector.connect(
    host="localhost",
    user="root",
    password="labhugo",
    database="farmdigital"
)
cursor = banco.cursor()

PER_PAGE = 8  # Quantidade de itens por página

def corrigir_input(data):  # Remoção de símbolos especiais de input
    return re.sub(r'\D', '', data)

def corrigir_data(data):  # Corrigir a data para o padrão DIA/MES/ANO
    if isinstance(data, date):
        data = data.strftime('%Y-%m-%d')
        datas = data.split('-')

        ano = datas[0]
        mes = datas[1]
        dia = datas[2]
        data_corrigida = dia + '/' + mes + '/' + ano

    return data_corrigida

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/home')  # Página Principal
def home():
    page = request.args.get('page', 1, type=int)  # Página atual (por padrão, será a primeira página)
    offset = (page - 1) * PER_PAGE  # Obtém os itens da página atual

    cursor.execute("SELECT produtos.nome, produtos.imagem, produtos.valor, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra LEFT JOIN promocao ON produtos.cod = promocao.cod_produtos WHERE promocao.cod_produtos IS NULL GROUP BY produtos.nome, produtos.imagem, produtos.valor ORDER BY valor DESC LIMIT %s OFFSET %s;", (PER_PAGE, offset))

    dados_produtos = []
    for linha in cursor.fetchall():
        nome_produto = linha[0]
        imagem_produto = base64.b64encode(linha[1]).decode('utf-8')
        valor_produto = str(linha[2]).replace('.', ',')
        avaliacao = float(linha[3]) if linha[3] else None
        quant_aval = linha[4] if linha[4] else 0

        produtos = {"nome": nome_produto,
                    "foto": imagem_produto,
                    "valor": valor_produto,
                    "avaliacao": avaliacao,
                    "quantidade": quant_aval}

        dados_produtos.append(produtos)

    cursor.execute("SELECT COUNT(*) FROM produtos;")
    quantidade = cursor.fetchone()
    total_produtos = quantidade[0] if quantidade else 0

    pagination = Pagination(page = page, per_page = PER_PAGE, total = total_produtos, css_framework = 'bootstrap3')  # Configuração da paginação
    mensagem = request.args.get('mensagem', '') # Extrai a mensagem da URL e a passa para o template home.html.

    if 'user_id' not in session:
        return render_template("principal.html", products=dados_produtos, pagination=pagination, promo = False, mensagem = mensagem)
    
    cursor.execute("SELECT nome FROM cliente WHERE email = %s;", (session['user_id'],))
    linha = cursor.fetchone()
    usuario = linha[0].split()

    return render_template("principal.html", products = dados_produtos, pagination = pagination, user = usuario[0], promo = False, mensagem = mensagem)

@app.route('/home/<tipo>', methods=['GET']) # Página com os produtos de cada categoria
def home_product(tipo): 
    page = request.args.get('page', 1, type=int)  # Página atual (por padrão, será a primeira página)
    offset = (page - 1) * PER_PAGE  # Obtém os itens da página atual

    cursor.execute("SELECT produtos.nome, produtos.imagem, produtos.valor, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra LEFT JOIN promocao ON produtos.cod = promocao.cod_produtos WHERE promocao.cod_produtos IS NULL AND categoria = %s GROUP BY produtos.nome, produtos.imagem, produtos.valor ORDER BY valor DESC LIMIT %s OFFSET %s;", (tipo, PER_PAGE, offset))

    dados_produtos = []
    for linha in cursor.fetchall():
        nome_produto = linha[0]
        imagem_produto = base64.b64encode(linha[1]).decode('utf-8')
        valor_produto = str(linha[2]).replace('.', ',')
        avaliacao = float(linha[3]) if linha[3] else None
        quant_aval = linha[4] if linha[4] else 0

        produtos = {"nome": nome_produto,
                    "foto": imagem_produto,
                    "valor": valor_produto,
                    "avaliacao": avaliacao,
                    "quantidade": quant_aval}

        dados_produtos.append(produtos)

    cursor.execute("SELECT COUNT(*) FROM produtos WHERE categoria = %s;", (tipo, ))
    quantidade = cursor.fetchone()
    total_produtos = quantidade[0] if quantidade else 0

    pagination = Pagination(page = page, per_page = PER_PAGE, total = total_produtos, css_framework = 'bootstrap3')  # Configuração da paginação

    if 'user_id' not in session:
        return render_template("principal.html", products=dados_produtos, pagination=pagination, promo = False)

    cursor.execute("SELECT nome FROM cliente WHERE email = %s;", (session['user_id'],))
    linha = cursor.fetchone()
    usuario = linha[0].split()

    return render_template("principal.html", products = dados_produtos, pagination = pagination, user = usuario[0], promo = False)

@app.route('/promocoes', methods=['GET'])   # Página com as promoções
def promocoes():
    page = request.args.get('page', 1, type=int)  # Página atual (por padrão, será a primeira página)
    offset = (page - 1) * PER_PAGE  # Obtém os itens da página atual

    cursor.execute("SELECT produtos.nome, produtos.imagem, produtos.valor, promocao.desconto, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos JOIN promocao ON produtos.cod = promocao.cod_produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra GROUP BY produtos.nome, produtos.imagem, produtos.valor, promocao.desconto ORDER BY valor DESC LIMIT %s OFFSET %s;", (PER_PAGE, offset)) # Selecionar os valores da tabela produtos que TEM correspondencia na tabela promocao

    dados_produtos = []
    for linha in cursor.fetchall():
        nome_produto = linha[0]
        imagem_produto = base64.b64encode(linha[1]).decode('utf-8')
        valor_produto = str(linha[2]).replace('.', ',')
        desconto = str("{:.0f}".format(linha[3] * 100))
        valor_desconto = str("{:.2f}".format(linha[2] * (1 - linha[3]))).replace('.', ',')
        avaliacao = float(linha[4]) if linha[4] else None
        quant_aval = linha[5] if linha[5] else 0


        produtos = {"nome": nome_produto,
                    "foto": imagem_produto,
                    "valor": valor_produto,
                    "desconto": desconto,
                    "novo_valor": valor_desconto,
                    "avaliacao": avaliacao,
                    "quantidade": quant_aval}

        dados_produtos.append(produtos)

    cursor.execute("SELECT COUNT(*) FROM produtos, promocao WHERE produtos.cod = promocao.cod_produtos;")
    quantidade = cursor.fetchone()
    total_produtos = quantidade[0] if quantidade else 0

    pagination = Pagination(page = page, per_page = PER_PAGE, total = total_produtos, css_framework = 'bootstrap3')  # Configuração da paginação

    if 'user_id' not in session:
        return render_template("principal.html", products=dados_produtos, pagination=pagination, promo = True)

    cursor.execute("SELECT nome FROM cliente WHERE email = %s;", (session['user_id'],))
    linha = cursor.fetchone()
    usuario = linha[0].split()

    return render_template("principal.html", products = dados_produtos, pagination = pagination, user = usuario[0], promo = True)

@app.route('/sign-up', methods=['GET', 'POST'])  # Cadastro de usuários
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
        senha = generate_password_hash(request.form['senha']) #Criptografar senha
        telefone = request.form.getlist('phone')
        foto = request.files['imagem']

        imagem = foto.read() #Converter a imagem em binário

        cursor.execute("SELECT email, cpf FROM cliente WHERE email = %s OR cpf = %s;", (email, cpf))

        if cursor.fetchone():
            return redirect(url_for('home', mensagem = "O usuário já existe!"))
        else:
            cursor.execute("INSERT INTO cliente VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (email, cpf, senha, nome, estado, cidade, bairro, rua, numero, nascimento, imagem))
            banco.commit()

            for i in telefone:
                i2 = corrigir_input(i)
                cursor.execute("INSERT INTO contato_cliente VALUES (%s, %s);", (i2, email))
                banco.commit()
            return redirect(url_for('home', mensagem = "Usuário cadastrado com sucesso!"))
    else:
        return render_template("sign-up.html")

@app.route('/log-in', methods=['GET', 'POST'])  # Login do usuário
def login():
    if request.method == 'POST':
        email = request.form['mail']
        senha = request.form['senha']

        cursor.execute("SELECT email, senha FROM cliente WHERE email = %s;", (email,))
        linha = cursor.fetchone()

        if linha and check_password_hash(linha[1], senha):
            session['user_id'] = linha[0]
            return redirect(url_for('home'))
        else:
            return render_template("log-in.html", mensagem="Parece que não existe um usuário com essas credenciais. Confira seus dados e tente novamente!")
    else:
        return render_template("log-in.html")

@app.route('/log-out')  # Logout do usuário
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/usuario', methods=['GET']) # Página com os dados do usuário
def usuario():
    email = session['user_id']

    cursor.execute("SELECT cliente.foto, cliente.nome, cliente.estado, cliente.cidade, cliente.bairro, cliente.rua, cliente.numero FROM cliente WHERE cliente.email = %s;", (email, ))
    linha = cursor.fetchone()

    foto_cliente = base64.b64encode(linha[0]).decode('utf-8') # Converter os dados binários em uma imagem
    nome_cliente = linha[1]
    estado_cliente = linha[2]
    cidade_cliente = linha[3]
    bairro_cliente = linha[4]
    rua_cliente = linha[5]
    numero_cliente = linha[6]

    return render_template("usuario.html", foto = foto_cliente, nome = nome_cliente, estado = estado_cliente, cidade = cidade_cliente, bairro = bairro_cliente, rua = rua_cliente, numero = numero_cliente)

@app.route('/produto/<nome>', methods=['GET'])  # Produto
def mostrar_produtos(nome):
    cursor.execute("SELECT produtos.nome, produtos.valor, produtos.quantidade, produtos.categoria, produtos.imagem, produtos.cod, promocao.desconto, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos LEFT JOIN promocao ON produtos.cod = promocao.cod_produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra WHERE produtos.nome = %s GROUP BY produtos.nome, produtos.valor, produtos.quantidade, produtos.categoria, produtos.imagem, produtos.cod, promocao.desconto;", (nome, ))
    linha = cursor.fetchone()

    nome_prod = linha[0]
    valor_prod = str("{:.2f}".format(linha[1] * (1 - linha[6]))).replace('.', ',') if linha[6] else str(linha[1]).replace('.', ',')
    quantidade_prod = linha[2]
    categoria_prod = linha[3]
    foto_prod = base64.b64encode(linha[4]).decode('utf-8') # Converter os dados binários em uma imagem
    cod_prod = linha[5]
    nota_prod = float(linha[7]) if linha[7] else None
    quant_aval = linha[8] if linha[8] else 0

    produto = {
        "nota": nota_prod,
        "quantidade": quant_aval}
    
    avaliacoes = []
    
    cursor.execute("SELECT avaliacao.descricao, avaliacao.nota, cliente.nome, compra.data FROM avaliacao JOIN compra ON compra.cod_compra = avaliacao.compra_cod JOIN produtos ON produtos.cod = compra.cod_produtos JOIN cliente ON cliente.email = compra.email_cliente WHERE produtos.nome = %s ORDER BY compra.data DESC;", (nome, ))
    linha2 = cursor.fetchall()

    for info in linha2:
        descricao, nota, nome_cliente, data_compra = info
        avaliacoes.append({
            'nome_cliente': nome_cliente,
            'data_compra': corrigir_data(data_compra),
            'descricao': descricao,
            'nota': float(nota)})

    return render_template("produto.html", nome2 = nome_prod, valor2 = valor_prod, quantidade2 = quantidade_prod, categoria2 = categoria_prod, foto2 = foto_prod, codigo2 = cod_prod, produto = produto, avaliacoes = avaliacoes)

@app.route('/produto', methods=['GET', 'POST'])  # Produto pesquisado
def mostrar_produto_pesquisado():
    if request.method == 'POST':
        nomeproduto = request.form['search']

        cursor.execute("SELECT produtos.nome, produtos.valor, produtos.quantidade, produtos.categoria, produtos.imagem, produtos.cod, promocao.desconto, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos LEFT JOIN promocao ON produtos.cod = promocao.cod_produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra WHERE produtos.nome = %s GROUP BY produtos.nome, produtos.valor, produtos.quantidade, produtos.categoria, produtos.imagem, produtos.cod, promocao.desconto;", (nomeproduto, ))
        linha = cursor.fetchone()

        if linha:
            nome_prod = linha[0]
            valor_prod = str("{:.2f}".format(linha[1] * (1 - linha[6]))).replace('.', ',') if linha[6] else str(linha[1]).replace('.', ',')
            quantidade_prod = linha[2]
            categoria_prod = linha[3]
            foto_prod = base64.b64encode(linha[4]).decode('utf-8') # Converter os dados binários em uma imagem
            cod_prod = linha[5]
            nota_prod = float(linha[7]) if linha[7] else None
            quant_aval = linha[8] if linha[8] else 0

            produto = {
                "nota": nota_prod,
                "quantidade": quant_aval}

            avaliacoes = []
    
            cursor.execute("SELECT avaliacao.descricao, avaliacao.nota, cliente.nome, compra.data FROM avaliacao JOIN compra ON compra.cod_compra = avaliacao.compra_cod JOIN produtos ON produtos.cod = compra.cod_produtos JOIN cliente ON cliente.email = compra.email_cliente WHERE produtos.nome = %s ORDER BY compra.data DESC;", (nomeproduto, ))
            linha2 = cursor.fetchall()

            for info in linha2:
                descricao, nota, nome_cliente, data_compra = info
                avaliacoes.append({
                    'nome_cliente': nome_cliente,
                    'data_compra': corrigir_data(data_compra),
                    'descricao': descricao,
                    'nota': float(nota)}) 

            return render_template("produto.html", nome2 = nome_prod, valor2 = valor_prod, quantidade2 = quantidade_prod, categoria2 = categoria_prod, foto2 = foto_prod, codigo2 = cod_prod, produto = produto, avaliacoes = avaliacoes)
        else:
            return redirect(url_for('home'))
    else:
        return render_template("produto.html", nome2 = "", valor2 = "", quantidade2 = "", categoria2 = "", foto2 = "", codigo2 = "")

@app.route('/save-product/<codigo>', methods=['POST']) # Salvar o produto no carrinho
def save_product(codigo):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    quantidade = request.form['quant']

    cursor.execute("INSERT INTO carrinho (cod_produtos, email_cliente, quantidade) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantidade = quantidade + VALUES(quantidade);", (codigo, user_id, quantidade))
    banco.commit()

    return redirect(url_for('home', mensagem = "Produto adicionado ao carrinho!"))

@app.route('/carrinho', methods=['GET'])  # Verificar carrinho
def carrinho():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    dados_carrinho = []
    total = 0

    cursor.execute("SELECT produtos.nome, produtos.cod, produtos.imagem, produtos.valor, carrinho.quantidade, promocao.desconto FROM produtos JOIN carrinho ON carrinho.cod_produtos = produtos.cod LEFT JOIN promocao ON promocao.cod_produtos = produtos.cod WHERE carrinho.email_cliente = %s;", (user_id,))

    for linha in cursor.fetchall():
        nome_produto = linha[0]
        cod_produto = linha[1]
        imagem_produto = base64.b64encode(linha[2]).decode('utf-8')
        valor_produto = str("{:.2f}".format(linha[3] * (1 - linha[5]))).replace('.', ',') if linha[5] else str(linha[3]).replace('.', ',')
        quant_produto = linha[4]
        total += ((linha[3] * (1 - linha[5])) * linha[4]) if linha[5] else (linha[3] * linha[4])

        produtos = {"nome": nome_produto,
                    "codigo": cod_produto,
                    "foto": imagem_produto,
                    "valor": valor_produto,
                    "quantidade": quant_produto}

        dados_carrinho.append(produtos)
    mensagem = request.args.get('mensagem', '')

    return render_template("carrinho.html", products=dados_carrinho, total=str(total).replace('.', ','), mensagem = mensagem)

@app.route('/update-quantity', methods=['POST']) # Atualizar quantidade de produtos no carrinho
def update_quantity():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    data = request.get_json()
    product_id = data['product_id']
    new_quantity = data['quantity']

    cursor.execute("UPDATE carrinho SET quantidade = %s WHERE email_cliente = %s AND cod_produtos = %s;",
                   (new_quantity, user_id, product_id))
    banco.commit()

    return jsonify({'success': True, 'new_quantity': new_quantity}), 200

@app.route('/comprar', methods=['POST'])  # Realizar compra
def comprar():
    cpf = corrigir_input(request.form['cpf'])
    senha = request.form['senha']
    user_id = session['user_id']
    codigos = request.form.getlist('codigos')

    hoje = datetime.date.today()

    cursor.execute("SELECT senha FROM cliente WHERE email = %s AND cpf = %s;", (user_id, cpf))
    linha = cursor.fetchone()

    if linha and check_password_hash(linha[0], senha):
        for i in codigos:
            cursor.execute("SELECT produtos.valor, carrinho.quantidade, produtos.quantidade, promocao.desconto FROM produtos JOIN carrinho ON carrinho.cod_produtos = produtos.cod LEFT JOIN promocao ON promocao.cod_produtos = produtos.cod WHERE carrinho.cod_produtos = %s AND carrinho.email_cliente = %s;", (i, user_id))
            linha = cursor.fetchone()

            valor_total = float("{:.2f}".format(linha[0] * (1 - linha[3]))) * linha[1] if linha[3] else linha[0] * linha[1] 
            estoque = linha[2] - linha[1]

            cursor.execute("INSERT INTO compra(email_cliente, cod_produtos, valor, data) VALUES (%s, %s, %s, %s);", (user_id, i, valor_total, hoje))
            cursor.execute("DELETE FROM carrinho WHERE cod_produtos = %s AND email_cliente = %s;", (i, user_id))
            cursor.execute("UPDATE produtos SET quantidade = %s WHERE cod = %s;", (estoque, i))
            banco.commit()

        return redirect(url_for('home', mensagem = "Compra realizada com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem = "Dados incorretos! Tente novamente mais tarde."))

@app.route('/comprados', methods=['GET'])   # Verificar compras feitas
def comprados():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    cursor.execute("SELECT produtos.nome, compra.cod_compra, produtos.imagem, compra.valor, compra.data, avaliacao.nota FROM produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra WHERE compra.email_cliente = %s ORDER BY compra.cod_compra DESC;", (user_id,))

    resultados = cursor.fetchall()

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
        cursor.execute("INSERT INTO avaliacao VALUES (%s, %s, %s);", (cod, estrela, texto))
        banco.commit()
        return redirect(url_for('home', mensagem = "Compra avaliada com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem = "Avaliação inválida!"))
    
@app.route('/reavaliar/<cod>', methods=['POST'])   # Verificar compras feitas
def reavaliar(cod):
    texto = request.form['avalie']
    estrela = request.form['estrela']

    if estrela:
        cursor.execute("UPDATE avaliacao SET nota = %s, descricao = %s WHERE compra_cod = %s;", (estrela, texto, cod))
        banco.commit()
        return redirect(url_for('home', mensagem = "Compra avaliada com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem = "Avaliação inválida!"))

if __name__ == "__main__":
    app.run(debug=True)