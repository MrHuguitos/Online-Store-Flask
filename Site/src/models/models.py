import src.dbconfig.dbconfig as db
import src.etc.corrigir as corrigir
import src.controller.controller as controller

def user_verification(user_id):
    conexao, cursor = db.conexao()    # Obtém conexão e cursor
    try:
        cursor.execute("SELECT nome FROM cliente WHERE email = %s;", (user_id,))
        linha = cursor.fetchone()
    finally:
        cursor.close()     # Fecha o cursor para liberar recursos
        conexao.close()    # Fecha a conexão com o banco
    
    return linha[0].split() if linha else None

def produtos_listagem(per_page, offset, tipo):
    conexao, cursor = db.conexao()
    promocao = False

    if tipo != False:
        try:
            cursor.execute("SELECT produtos.nome, produtos.imagem, produtos.valor, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra LEFT JOIN promocao ON produtos.cod = promocao.cod_produtos WHERE promocao.cod_produtos IS NULL AND categoria = %s GROUP BY produtos.nome, produtos.imagem, produtos.valor ORDER BY valor DESC LIMIT %s OFFSET %s;", (tipo, per_page, offset))
            linhas = cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()
    else:
        try:
            cursor.execute("SELECT produtos.nome, produtos.imagem, produtos.valor, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra LEFT JOIN promocao ON produtos.cod = promocao.cod_produtos WHERE promocao.cod_produtos IS NULL GROUP BY produtos.nome, produtos.imagem, produtos.valor ORDER BY valor DESC LIMIT %s OFFSET %s;", (per_page, offset))
            linhas = cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    return controller.listar_produtos(linhas, promocao)

def quant_produtos(tipo):
    conexao, cursor = db.conexao()
    if tipo != False:
        try:
            cursor.execute("SELECT COUNT(*) FROM produtos WHERE categoria = %s;", (tipo, ))
            quant = cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()
    else:
        try:
            cursor.execute("SELECT COUNT(*) FROM produtos;")
            quant = cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    return quant[0] if quant else 0

def produtos_promocao(per_page, offset):
    conexao, cursor = db.conexao()
    promocao = True
    try:
        cursor.execute("SELECT produtos.nome, produtos.imagem, produtos.valor, promocao.desconto, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos JOIN promocao ON produtos.cod = promocao.cod_produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra GROUP BY produtos.nome, produtos.imagem, produtos.valor, promocao.desconto ORDER BY valor DESC LIMIT %s OFFSET %s;", (per_page, offset))
        linhas = cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()

    return controller.listar_produtos(linhas, promocao)

def quant_prod_promocao():
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT COUNT(*) FROM produtos, promocao WHERE produtos.cod = promocao.cod_produtos;")
        quant = cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()

    return quant[0] if quant else 0

def verificar_cadastro(email, cpf):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT email, cpf FROM cliente WHERE email = %s OR cpf = %s;", (email, cpf))
        linha = cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()

    return True if linha else False

def cadastrar_user(email, cpf, senha, nome, estado, cidade, bairro, rua, numero, nascimento, imagem, telefone):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("INSERT INTO cliente VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (email, cpf, senha, nome, estado, cidade, bairro, rua, numero, nascimento, imagem))
        for i in telefone:
            i2 = corrigir.corrigir_input(i)
            cursor.execute("INSERT INTO contato_cliente VALUES (%s, %s);", (i2, email))
            conexao.commit()
        conexao.commit()

        mensagem = "Usuário cadastrado com sucesso!"
    except Exception as e:
        mensagem = f"Ocorreu um erro: {e}. Tente novamente mais tarde."
    finally:
        cursor.close()
        conexao.close()

    return mensagem

def login_user(email, cpf):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT email, cpf, senha FROM cliente WHERE email = %s AND cpf = %s;", (email, cpf))
        linha = cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()

    return linha if linha else None

def dados_perfil(email):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT cliente.foto, cliente.nome, cliente.estado, cliente.cidade, cliente.bairro, cliente.rua, cliente.numero FROM cliente WHERE cliente.email = %s;", (email, ))
        linha = cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()

    return linha

def produtos_info(nome):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT produtos.nome, produtos.valor, produtos.quantidade, produtos.categoria, produtos.imagem, produtos.cod, promocao.desconto, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos LEFT JOIN promocao ON produtos.cod = promocao.cod_produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra WHERE produtos.nome = %s GROUP BY produtos.nome, produtos.valor, produtos.quantidade, produtos.categoria, produtos.imagem, produtos.cod, promocao.desconto;", (nome, ))
        linha = cursor.fetchone()
    finally:
        cursor.close()
        conexao.close() 

    return linha   

def produtos_aval(nome):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT avaliacao.descricao, avaliacao.nota, cliente.nome, compra.data FROM avaliacao JOIN compra ON compra.cod_compra = avaliacao.compra_cod JOIN produtos ON produtos.cod = compra.cod_produtos JOIN cliente ON cliente.email = compra.email_cliente WHERE produtos.nome = %s ORDER BY compra.data DESC;", (nome, ))
        linha = cursor.fetchall()
    finally:
        cursor.close()
        conexao.close() 

    return linha

def save_product(codigo, user_id, quantidade):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("INSERT INTO carrinho (cod_produtos, email_cliente, quantidade) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantidade = quantidade + VALUES(quantidade);", (codigo, user_id, quantidade))
        conexao.commit()
        mensagem = "Produto adicionado ao carrinho!"
    except Exception as e:
        mensagem = f"Ocorreu um erro: {e}. Tente novamente mais tarde."
    finally:
        cursor.close()
        conexao.close()

    return mensagem
