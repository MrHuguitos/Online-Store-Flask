import base64
import src.models.models as models
import src.etc.corrigir as corrigir
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# Página Principal
def listar_produtos(products, promocao):
    dados_produtos = []
    for linha in products:
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

        if promocao == True: # Caso o produto esteja em promoção
            produtos.update({
                "desconto": str("{:.0f}".format(linha[3] * 100)),
                "novo_valor": str("{:.2f}".format(linha[2] * (1 - linha[3]))).replace('.', ','),
            })

        dados_produtos.append(produtos)

    return dados_produtos

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