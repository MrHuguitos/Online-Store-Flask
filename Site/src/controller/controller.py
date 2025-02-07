import base64
import datetime
import src.models.models as models
import src.etc.corrigir as corrigir
from datetime import date
from flask_paginate import Pagination
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

PER_PAGE = 8  # Quantidade de itens por página

# Página Principal
def listar_produtos(tipo, promocao):
    page = request.args.get('page', 1, type=int)                     # Página atual, que por padrão será a primeira página
    offset = (page - 1) * PER_PAGE                                   # Obtém os itens da página atual
    dados_produtos = []

    if promocao == False:
        produtos_lista = models.produtos_listagem(PER_PAGE, offset, tipo)   # Obter todos os produtos, com suas devidas informações
        produtos_quant = models.quant_produtos(tipo)                        # Obter a quantidade de produtos diferentes cadastrados

        for linha in produtos_lista:
            nome = linha[0]
            imagem = base64.b64encode(linha[1]).decode('utf-8')
            valor = str(linha[2]).replace('.', ',')
            avaliacao = float(linha[3]) if linha[3] else None
            quant_aval = linha[4] if linha[4] else 0

            produtos = {"nome": nome,
                        "foto": imagem,
                        "valor": valor,
                        "avaliacao": avaliacao,
                        "quantidade": quant_aval}
            
            dados_produtos.append(produtos)

        pagination = Pagination(page=page, per_page=PER_PAGE, total=produtos_quant, css_framework='bootstrap3')
        mensagem = request.args.get('mensagem', '')  # Extrai a mensagem da URL e a passa para o template home.html

        if 'user_id' not in session:
            return render_template("principal.html", products=dados_produtos, pagination=pagination, promo=False, mensagem=mensagem)

        user = models.user_verification(session['user_id'])

        return render_template("principal.html", products=dados_produtos, pagination=pagination, user=user[0], promo=False, mensagem=mensagem)
    else:
        produtos_lista = models.produtos_promocao(PER_PAGE, offset)   # Obter todos os produtos, com suas devidas informações
        produtos_quant = models.quant_prod_promocao()                       # Obter a quantidade de produtos diferentes cadastrados

        for linha in produtos_lista:
            nome = linha[0]
            imagem = base64.b64encode(linha[1]).decode('utf-8')
            valor = str(linha[2]).replace('.', ',')
            novo_valor = str("{:.2f}".format(linha[2] * (1 - linha[3]))).replace('.', ',')
            desconto = str("{:.0f}".format(linha[3] * 100))
            avaliacao = float(linha[3]) if linha[3] else None
            quant_aval = linha[4] if linha[4] else 0

            produtos = {"nome": nome,
                        "foto": imagem,
                        "valor": valor,
                        "novo_valor": novo_valor,
                        "desconto": desconto,
                        "avaliacao": avaliacao,
                        "quantidade": quant_aval}
            
            dados_produtos.append(produtos)

        pagination = Pagination(page=page, per_page=PER_PAGE, total=produtos_quant, css_framework='bootstrap3')
        mensagem = request.args.get('mensagem', '')  # Extrai a mensagem da URL e a passa para o template home.html

        if 'user_id' not in session:
            return render_template("principal.html", products=dados_produtos, pagination=pagination, promo=True, mensagem=mensagem)

        user = models.user_verification(session['user_id'])

        return render_template("principal.html", products=dados_produtos, pagination=pagination, user=user[0], promo=True, mesagem=mensagem)

# Sig-up
def sigup():
    email = request.form['mail']
    cpf = corrigir.corrigir_input(request.form['cpf'])
    nome = request.form['nome']
    nascimento = request.form['nascimento']
    estado = request.form['state']
    cidade = request.form['city']
    bairro = request.form['district']
    rua = request.form['street']
    numero = request.form['number']
    senha = generate_password_hash(request.form['senha'])  # Criptografar senha
    telefone = request.form.getlist('phone')
    imagem = request.files['imagem']
    img_bin = imagem.read()

    if (models.verificar_cadastro(email, cpf)) == True:
        return redirect(url_for('home', mensagem="O usuário já existe!"))
    else:
        text = models.cadastrar_user(email, cpf, senha, nome, estado, cidade, bairro, rua, numero, nascimento, img_bin, telefone)
        return redirect(url_for('home', mensagem=text))

# Login
def login():
    email = request.form['mail']
    cpf = corrigir.corrigir_input(request.form['cpf'])
    senha = request.form['senha']

    dados = models.login_user(email, cpf)

    if dados is not None and check_password_hash(dados[2], senha):
        session['user_id'] = dados[0]
        return redirect(url_for('home', mensagem="Login realizado com sucesso!"))
    else:
        return render_template("log-in.html", mensagem="Parece que não existe um usuário com essas credenciais. Confira seus dados e tente novamente!")

# Perfil
def perfil():
    email = session['user_id']
    dados = models.dados_perfil(email)

    foto_cliente = base64.b64encode(dados[0]).decode('utf-8')  # Converter os dados binários em uma imagem
    nome_cliente = dados[1]
    estado_cliente = dados[2]
    cidade_cliente = dados[3]
    bairro_cliente = dados[4]
    rua_cliente = dados[5]
    numero_cliente = dados[6]

    return render_template("usuario.html", foto=foto_cliente, nome=nome_cliente, estado=estado_cliente, cidade=cidade_cliente, bairro=bairro_cliente, rua=rua_cliente, numero=numero_cliente)

# Produto
def produto(nome):
    dados = models.produtos_info(nome)
    if dados:
        nome = dados[0]
        valor = str("{:.2f}".format(dados[1] * (1 - dados[6]))).replace('.', ',') if dados[6] else str(dados[1]).replace('.', ',')
        quantidade = dados[2]
        categoria = dados[3]
        imagem = base64.b64encode(dados[4]).decode('utf-8') # Converter os dados binários em uma imagem
        codigo = dados[5]
        nota = float(dados[7]) if dados[7] else None
        quant_aval = dados[8] if dados[8] else 0

        feedbacks = {
            "nota": nota,
            "quantidade": quant_aval}

        avaliacoes = []

        dados_aval = models.produtos_aval(nome)

        for info in dados_aval:
            descricao, nota_cliente, nome_cliente, data_compra = info
            avaliacoes.append({
                'nome_cliente': nome_cliente,
                'data_compra': corrigir.corrigir_data(data_compra),
                'descricao': descricao,
                'nota': float(nota_cliente)})

        return render_template("produto.html", nome2=nome, valor2=valor, quantidade2=quantidade, categoria2=categoria, foto2=imagem, codigo2=codigo, produto=feedbacks, avaliacoes=avaliacoes)
    else:
        return redirect(url_for('home', mensagem="O produto não está disponível"))

# Salvar Produto
def salvar_produtos(codigo):
    user_id = session['user_id']
    quantidade = request.form['quant']

    dados = models.save_product(codigo, user_id, quantidade)

    return redirect(url_for('home', mensagem=dados))

# Carrinho
def carrinho():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    dados_carrinho = []
    total = 0

    dados = models.carrinho_info(user_id)

    for linha in dados:
        nome = linha[0]
        codigo = linha[1]
        imagem = base64.b64encode(linha[2]).decode('utf-8')
        valor = str("{:.2f}".format(linha[3] * (1 - linha[5]))).replace('.', ',') if linha[5] else str(linha[3]).replace('.', ',')
        quantidade = linha[4]
        total += ((linha[3] * (1 - linha[5])) * linha[4]) if linha[5] else (linha[3] * linha[4]) # Soma do valor de todos os itens no carrinho

        produtos = {"nome": nome,
                    "codigo": codigo,
                    "foto": imagem,
                    "valor": valor,
                    "quantidade": quantidade}

        dados_carrinho.append(produtos)

    mensagem = request.args.get('mensagem', '')

    return render_template("carrinho.html", products=dados_carrinho, total=str(total).replace('.', ','), mensagem=mensagem)

# Atualizar quantidade
def put_quantidade():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    data = request.get_json()
    product_id = data['product_id']
    new_quantity = data['quantity']

    dados = models.atualizar_quant(new_quantity, user_id, product_id)

    if dados == True:
        return jsonify({'success': True, 'new_quantity': new_quantity}), 200
    else:
        return jsonify({'success': False, 'new_quantity': new_quantity}), 500

# Realizar compra
def comprar_produto():
    cpf = corrigir.corrigir_input(request.form['cpf'])
    senha = request.form['senha']
    user_id = session['user_id']
    codigos = request.form.getlist('codigos') # Obter o código de todos os produtos do carrinho
    hoje = datetime.date.today() # Obter a data de hoje

    dados = models.login_user(user_id, cpf)

    if dados and check_password_hash(dados[2], senha):
        for i in codigos:
            dados2 = models.compra_produtos(i, user_id)
            valor_total = float("{:.2f}".format(dados2[0] * (1 - dados2[3]))) * dados2[1] if dados2[3] else dados2[0] * dados2[1]
            estoque = dados2[2] - dados2[1]
            compra = models.finalizar_compra(user_id, i, valor_total, hoje, estoque)

            if compra != True:
                return redirect(url_for('home', mensagem=compra))
            else:
                pass

        return redirect(url_for('home', mensagem="Compras realizadas com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem="Dados incorretos! Tente novamente mais tarde."))

# Histórico de compras
def historico():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    dados_compra = []
    user_id = session['user_id']
    dados = models.verificar_compras(user_id)

    for linha in dados:
        nome = linha[0]
        codigo = linha[1]
        imagem = base64.b64encode(linha[2]).decode('utf-8')
        valor = str(linha[3]).replace('.', ',')
        data = corrigir.corrigir_data(linha[4])
        avaliacao = linha[5] if linha[5] else None

        produtos = {"nome": nome,
                    "codigo_compra": codigo,
                    "foto": imagem,
                    "valor": valor,
                    "data": data,
                    "avaliacao": avaliacao}

        dados_compra.append(produtos)

    return render_template("compras.html", products=dados_compra)

# Avaliar Produto
def avaliar(cod, funcao):
    texto = request.form['avalie']
    estrela = request.form['estrela']

    if (estrela) and (funcao == "avaliar"):
        dados = models.inserir_aval(cod, estrela, texto, "avaliar")

        if dados != True:
            return redirect(url_for('home', mensagem=dados))
        else:
            return redirect(url_for('home', mensagem="Compra avaliada com sucesso!"))
    elif (estrela) and (funcao == "reavaliar"):
        dados = models.inserir_aval(cod, estrela, texto, "reavaliar")

        if dados != True:
            return redirect(url_for('home', mensagem=dados))
        else:
            return redirect(url_for('home', mensagem="Compra avaliada com sucesso!"))
    else:
        return redirect(url_for('carrinho', mensagem="Avaliação inválida!"))