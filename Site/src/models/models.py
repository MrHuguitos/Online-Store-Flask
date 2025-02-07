import src.dbconfig.dbconfig as db
import src.etc.corrigir as corrigir

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

    return linhas

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
    try:
        cursor.execute("SELECT produtos.nome, produtos.imagem, produtos.valor, promocao.desconto, AVG(avaliacao.nota), COUNT(avaliacao.nota) FROM produtos JOIN promocao ON produtos.cod = promocao.cod_produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra GROUP BY produtos.nome, produtos.imagem, produtos.valor, promocao.desconto ORDER BY valor DESC LIMIT %s OFFSET %s;", (per_page, offset))
        linhas = cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()

    return linhas

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

def carrinho_info(user_id):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT produtos.nome, produtos.cod, produtos.imagem, produtos.valor, carrinho.quantidade, promocao.desconto FROM produtos JOIN carrinho ON carrinho.cod_produtos = produtos.cod LEFT JOIN promocao ON promocao.cod_produtos = produtos.cod WHERE carrinho.email_cliente = %s;", (user_id,))
        linha = cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()

    return linha

def atualizar_quant(new_quantity, user_id, product_id):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("UPDATE carrinho SET quantidade = %s WHERE email_cliente = %s AND cod_produtos = %s;",(new_quantity, user_id, product_id))
        conexao.commit()
        mensagem = True
    except:
        mensagem = False
    finally:
        cursor.close()
        conexao.close()

    return mensagem

def compra_produtos(codigo, user_id):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT produtos.valor, carrinho.quantidade, produtos.quantidade, promocao.desconto FROM produtos JOIN carrinho ON carrinho.cod_produtos = produtos.cod LEFT JOIN promocao ON promocao.cod_produtos = produtos.cod WHERE carrinho.cod_produtos = %s AND carrinho.email_cliente = %s;", (codigo, user_id))
        linha = cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()

    return linha

def finalizar_compra(user_id, codigo, valor_total, data, estoque):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("INSERT INTO compra(email_cliente, cod_produtos, valor, data) VALUES (%s, %s, %s, %s);", (user_id, codigo, valor_total, data))
        cursor.execute("DELETE FROM carrinho WHERE cod_produtos = %s AND email_cliente = %s;", (codigo, user_id))
        cursor.execute("UPDATE produtos SET quantidade = %s WHERE cod = %s;", (estoque, codigo))
        conexao.commit()
        sucesso = True
    except Exception as e:
        sucesso = f"Ocorreu um erro: {e}. Tente novamente mais tarde."
    finally:
        cursor.close()
        conexao.close()

    return sucesso

def verificar_compras(user_id):
    conexao, cursor = db.conexao()
    try:
        cursor.execute("SELECT produtos.nome, compra.cod_compra, produtos.imagem, compra.valor, compra.data, avaliacao.nota FROM produtos JOIN compra ON compra.cod_produtos = produtos.cod LEFT JOIN avaliacao ON avaliacao.compra_cod = compra.cod_compra WHERE compra.email_cliente = %s ORDER BY compra.cod_compra DESC;", (user_id,))
        linha = cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()

    return linha

def inserir_aval(cod, estrela, texto, funcao):
    conexao, cursor = db.conexao()

    if funcao == "avaliar":
        try:
            cursor.execute("INSERT INTO avaliacao VALUES (%s, %s, %s);", (cod, estrela, texto))
            conexao.commit()
            sucesso = True
        except Exception as e:
            sucesso = f"Ocorreu um erro: {e}. Tente novamente mais tarde."
        finally:
            cursor.close()
            conexao.close()
    else:
        try:
            cursor.execute("UPDATE avaliacao SET nota = %s, descricao = %s WHERE compra_cod = %s;", (estrela, texto, cod))
            conexao.commit()
            sucesso = True
        except Exception as e:
            sucesso = f"Ocorreu um erro: {e}. Tente novamente mais tarde."
        finally:
            cursor.close()
            conexao.close()

    return sucesso