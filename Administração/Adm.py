from PySimpleGUI import PySimpleGUI as sg
import mysql.connector

def convert_to_binary(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    return binary_data

banco = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "labhugo",
    database = "farmdigital"
)
cursor = banco.cursor()

# Layout
sg.theme('Reddit')

layout_principal = [
    [sg.Button('Adicionar', size = (40, 5), font=('Helvetica', 20))],
    [sg.Button('Deletar', size = (40, 5), font=('Helvetica', 20))],
    [sg.Button('Editar', size = (40, 5), font=('Helvetica', 20))],
    [sg.Button('Promoções', size = (40, 5), font=('Helvetica', 20))]
]
def add_produtos():
    layout_add = [
        [sg.Text('Código:', font=('Helvetica', 15))], #Código
        [sg.Input(key='cod', size=(30, 10))],
        [sg.Text('Nome:', font=('Helvetica', 15))], #Nome
        [sg.Input(key='name', size = (30, 3))],
        [sg.Text('Quantidade:', font=('Helvetica', 15))], #Quantidade
        [sg.Spin([i for i in range(1, 999)], initial_value=1, key = 'number', size = (29, 3))],
        [sg.Text('Valor:', font=('Helvetica', 15))], #Valor
        [sg.Spin([i/100 for i in range(0, 100000)], key='money', size = (29, 3), initial_value=0.00)],
        [sg.Text('Categoria:', font=('Helvetica', 15))], #Categoria
        [sg.Combo(['Medicamentos', 'Vitaminas e Suplementos', 'Higiene Pessoal', 'Cosméticos', 'Infantil', 'Terceira Idade', 'Primeiros Socorros', 'Equipamentos de Saúde'], key='category', size = (29, 3))],
        [sg.Text('Imagem(PNG):', font=('Helvetica', 15)), sg.Input(key='file_path', enable_events=True, visible=False)], #Imagem
        [sg.FileBrowse('Descarregar', target='file_path', size = (20, 1))],
        [sg.Image(key='imagem', visible=False)],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Adicionar Produtos', layout_add, element_justification='center', finalize=True)
def del_produtos():
    layout_del = [
        [sg.Text('Código'), sg.Input(key='cod', size = (20, 1))],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Deletar Produtos', layout_del, element_justification='center', finalize=True)
def edit_produtos():
    layout_editor = [
        [sg.Button('Quantidade', size = (40, 5), font=('Helvetica', 20))],
        [sg.Button('Valor', size = (40, 5), font=('Helvetica', 20))],
        [sg.Button('Nome', size = (40, 5), font=('Helvetica', 20))],
        [sg.Button('Voltar', size = (40, 5), font=('Helvetica', 20))]
    ]
    return sg.Window('Editar Produtos', layout_editor, element_justification='center', finalize=True)
def edit_quant():
    layout_editor_quant = [
        [sg.Text('Código'), sg.Input(key='cod', size = (20, 1))],
        [sg.Text('Ação'), sg.Combo(['Adicionar', 'Remover'], key='action', size = (20, 1))],
        [sg.Text('Quantidade'), sg.Spin([i for i in range(1, 999)], initial_value=1, key = 'number', size = (20, 1))],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Editar Quantidade', layout_editor_quant, element_justification='center', finalize=True)
def edit_value():
    layout_editor_valor = [
        [sg.Text('Código'), sg.Input(key='cod', size = (20, 1))],
        [sg.Text('Valor'), sg.Spin([i/100 for i in range(0, 100000)], key='money', size = (20, 1), initial_value=0.00)],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Editar Valor', layout_editor_valor, element_justification='center', finalize=True)
def edit_name():
    layout_editor_nome = [
        [sg.Text('Código'), sg.Input(key='cod', size = (20, 1))],
        [sg.Text('Nome'), sg.Input(key='name', size = (20, 1))],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Editar Nome', layout_editor_nome, element_justification='center', finalize=True)
def promo_produtos():
    layout_promocoes = [
        [sg.Button('Adicionar', size = (40, 5), font=('Helvetica', 20))],
        [sg.Button('Editar', size = (40, 5), font=('Helvetica', 20))],
        [sg.Button('Fechar', size = (40, 5), font=('Helvetica', 20))],
        [sg.Button('Voltar', size = (40, 5), font=('Helvetica', 20))]
    ]
    return sg.Window('Promoções', layout_promocoes, element_justification='center', finalize=True)
def add_promo():
    layout_promocoes_add = [
        [sg.Text('Código'), sg.Input(key='cod', size = (20, 1))],
        [sg.Text('Desconto'), sg.Spin([i/100 for i in range(0, 10000)], key='desconto', size = (20, 1), initial_value=0.00)],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Criar Promoção', layout_promocoes_add, element_justification='center', finalize=True)
def edit_promo():
    layout_promocoes_edit = [
        [sg.Text('Código'), sg.Input(key='cod', size = (20, 1))],
        [sg.Text('Novo Desconto'), sg.Spin([i/100 for i in range(0, 10000)], key='new_desconto', size = (20, 1), initial_value=0.00)],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Editar Promoção', layout_promocoes_edit, element_justification='center', finalize=True)
def del_promo():
    layout_promocoes_dell = [
        [sg.Text('Código'), sg.Input(key='cod', size = (20, 1))],
        [sg.Button('Voltar'), sg.Button('Confirmar')]
    ]
    return sg.Window('Fechar Promoção', layout_promocoes_dell, element_justification='center', finalize=True)

# Janela
janela = sg.Window('Tela de Login', layout_principal, element_justification='center', finalize=True)
janela.maximize()

# Eventos
while True:
    eventos, valores = janela.read()
    if eventos == sg.WINDOW_CLOSED:
        break
    elif eventos == 'Adicionar':
        janela_add = add_produtos()
        janela_add.maximize()

        while True:
            eventos_add, valores_add = janela_add.read()
            if eventos_add == sg.WINDOW_CLOSED:
                break
            elif eventos_add == 'file_path':
                janela_add['imagem'].update(filename=valores_add['file_path'])
            elif eventos_add == 'Confirmar':
                codigo = valores_add['cod']
                nome = valores_add['name']
                quantidade = valores_add['number']
                valor = valores_add['money']
                categoria = valores_add['category']
                imagem = convert_to_binary(valores_add['file_path'])

                cursor.execute("SELECT * FROM produtos WHERE cod = %s;", (codigo,))
                linha = cursor.fetchone()

                if linha is not None:
                    sg.popup("O produto não pode ser cadastrado, pois já existe!")
                    janela_add.close()
                else: 
                    cursor.execute("INSERT INTO produtos VALUES (%s, %s, %s, %s, %s, %s);", (codigo, nome, quantidade, valor, categoria, imagem))
                    banco.commit()
                    sg.popup("Produto Cadastrado com Sucesso!")
                    janela_add.close()
            elif eventos_add == 'Voltar':
                janela_add.close()
                
                janela_add.close()
    elif eventos == 'Deletar':
        janela_del = del_produtos()
        janela_del.maximize()

        while True:
            eventos_del, valores_del = janela_del.read()
            if eventos_del == sg.WINDOW_CLOSED:
                break
            elif eventos_del == 'Confirmar':
                codigo = valores_del['cod']

                cursor.execute("SELECT * FROM produtos WHERE cod = %s;", (codigo,))
                linha = cursor.fetchone()

                if linha is not None: 
                    cursor.execute("DELETE FROM produtos WHERE cod = %s;", (codigo,))
                    banco.commit()
                    sg.popup("Produto Deletado com Sucesso!")
                    janela_del.close()
                else: 
                    sg.popup("O produto não pode ser deletado, pois não existe!")
                    janela_del.close()
                
                janela_del.close()
            elif eventos_del == 'Voltar':
                janela_del.close()

                janela_del.close()
    elif eventos == 'Editar':
        janela_editor = edit_produtos()
        janela_editor.maximize()

        while True:
            eventos_edit, valores_edit = janela_editor.read()
            if eventos_edit == sg.WINDOW_CLOSED:
                break
            elif eventos_edit == 'Quantidade':
                janela_editor_quant = edit_quant()
                janela_editor_quant.maximize()

                while True:
                    eventos_quant, valores_quant = janela_editor_quant.read()
                    if eventos_quant == sg.WINDOW_CLOSED:
                        break
                    elif eventos_quant == 'Confirmar':
                        codigo = valores_quant['cod']
                        acao = valores_quant['action']
                        quantidade = valores_quant['number']

                        cursor.execute("SELECT quantidade FROM produtos WHERE cod = %s;", (codigo,))
                        linha = cursor.fetchone()

                        if linha is not None:
                            if acao == 'Adicionar':
                                total = linha[0] + int(quantidade)
                                cursor.execute("UPDATE produtos SET quantidade = %s WHERE cod = %s;", (total, codigo))
                                banco.commit()
                                sg.popup("Produto Alterado com Sucesso!")
                                janela_editor_quant.close()
                            elif acao == 'Remover':
                                total = linha[0] - int(quantidade)
                                if total >= 0:
                                    cursor.execute("UPDATE produtos SET quantidade = %s WHERE cod = %s;", (total, codigo))
                                    banco.commit()
                                    sg.popup("Produto Alterado com Sucesso!")
                                    janela_editor_quant.close()
                                else:
                                    sg.popup("Alteração Inválida!")
                                    janela_editor_quant.close()
                        else: 
                            sg.popup("O produto não pode ser alterado, pois não existe!")
                            janela_editor_quant.close()
                    elif eventos_quant == 'Voltar':
                        janela_editor_quant.close()

                        janela_editor_quant.close()
            elif eventos_edit == 'Valor':
                janela_editor_valor = edit_value()
                janela_editor_valor.maximize()

                while True:
                    eventos_valor, valores_valor = janela_editor_valor.read()
                    if eventos_valor == sg.WINDOW_CLOSED:
                        break
                    elif eventos_valor == 'Confirmar':
                        codigo = valores_valor['cod']
                        valor = valores_valor['money']

                        cursor.execute("SELECT valor FROM produtos WHERE cod = %s;", (codigo,))
                        linha = cursor.fetchone()

                        if linha is not None:
                            if valor > 0: 
                                cursor.execute("UPDATE produtos SET valor = %s WHERE cod = %s;", (valor, codigo))
                                banco.commit()
                                sg.popup("Produto Alterado com Sucesso!")
                                janela_editor_valor.close()    
                            else:
                                sg.popup("Alteração Inválida!")
                                janela_editor_valor.close()
                        else: 
                            sg.popup("O produto não pode ser alterado, pois não existe!")
                            janela_editor_valor.close()
                    elif eventos_valor == 'Voltar':
                        janela_editor_valor.close()
                
                        janela_editor_valor.close()
            elif eventos_edit == 'Nome':
                janela_editor_nome = edit_name()
                janela_editor_nome.maximize()

                while True:
                    eventos_nome, valores_nome = janela_editor_nome.read()
                    if eventos_nome == sg.WINDOW_CLOSED:
                        break
                    elif eventos_nome == 'Confirmar':
                        codigo = valores_valor['cod']
                        nome = valores_valor['name']

                        cursor.execute("SELECT nome FROM produtos WHERE cod = %s;", (codigo,))
                        linha = cursor.fetchone()

                        if linha is not None:                            
                            cursor.execute("UPDATE produtos SET nome = %s WHERE cod = %s;", (nome, codigo))
                            banco.commit()
                            sg.popup("Produto Alterado com Sucesso!")
                            janela_editor_nome.close()    
                        else: 
                            sg.popup("O produto não pode ser alterado, pois não existe!")
                            janela_editor_nome.close()
                    elif eventos_nome == 'Voltar':
                        janela_editor_nome.close()
                
                        janela_editor_nome.close()
            elif eventos_edit == 'Voltar':
                janela_editor.close()

                janela_editor.close()
    elif eventos == 'Promoções':
        janela_promocoes = promo_produtos()
        janela_promocoes.maximize()

        while True:
            eventos_promocoes, valores_promocoes = janela_promocoes.read()
            if eventos_promocoes == sg.WINDOW_CLOSED:
                break
            elif eventos_promocoes == 'Adicionar':
                janela_promocoes_add = add_promo()
                janela_promocoes_add.maximize()

                while True:
                    eventos_promocoes_add, valores_promocoes_add = janela_promocoes_add.read()
                    if eventos_promocoes_add == sg.WINDOW_CLOSED:
                        break
                    elif eventos_promocoes_add == 'Confirmar':
                        codigo = valores_promocoes_add['cod']
                        desconto = valores_promocoes_add['desconto']

                        desconto_format = float("{:.2f}".format((float(desconto) / 100)))

                        if (1 - desconto_format) <= 0:
                            sg.popup("Operação Inválida!")
                        else:
                            cursor.execute("SELECT nome FROM produtos WHERE cod = %s;", (codigo,))
                            linha = cursor.fetchone()

                            if linha is not None:
                                cursor.execute(f"SELECT desconto FROM promocao WHERE cod_produtos = {codigo};")
                                linha2 = cursor.fetchone()
            
                                if linha2 is not None:
                                    sg.popup("A promoção já existe!")
                                    janela_promocoes_add.close()
                                else:
                                    cursor.execute("INSERT INTO promocao VALUES (%s, %s);", (codigo, desconto_format))
                                    banco.commit()
                                    sg.popup("Promoção Cadastrada com Sucesso!")
                                    janela_promocoes_add.close()
                            else: 
                                sg.popup("O promoção não pode ser criada, pois o produto não existe!")
                                janela_promocoes_add.close()
                    elif eventos_promocoes_add == 'Voltar':
                        janela_promocoes_add.close()

                        janela_promocoes_add.close()
            elif eventos_promocoes == 'Editar':
                janela_promocoes_edit = edit_promo()
                janela_promocoes_edit.maximize()

                while True:
                    eventos_promocoes_edit, valores_promocoes_edit = janela_promocoes_edit.read()
                    if eventos_promocoes_edit == sg.WINDOW_CLOSED:
                        break
                    elif eventos_promocoes_edit == 'Confirmar':
                        codigo = valores_promocoes_edit['cod']
                        desconto_novo = valores_promocoes_edit['new_desconto']

                        desconto_format = float("{:.2f}".format((float(desconto_novo) / 100)))

                        if (1 - desconto_format) <= 0:
                            sg.popup("Operação Inválida!")
                            janela_promocoes_edit.close()
                        else:
                            cursor.execute("SELECT cod_produtos FROM promocao WHERE cod_produtos = %s;", (codigo,))
                            linha = cursor.fetchone()

                            if linha is not None:
                                cursor.execute("UPDATE promocao SET desconto = %s WHERE cod_produtos = %s;", (desconto_format, codigo))
                                banco.commit()
                                sg.popup("Promoção Editada com Sucesso!")
                                janela_promocoes_edit.close()
                            else: 
                                sg.popup("O promoção não pode ser editada, pois não existe!")
                                janela_promocoes_edit.close()
                    elif eventos_promocoes_edit == 'Voltar':
                        janela_promocoes_edit.close()

                        janela_promocoes_edit.close()
            elif eventos_promocoes == 'Fechar':
                janela_promocoes_dell = del_promo()
                janela_promocoes_dell.maximize()

                while True:
                    eventos_promocoes_dell, valores_promocoes_dell = janela_promocoes_dell.read()
                    if eventos_promocoes_dell == sg.WINDOW_CLOSED:
                        break
                    elif eventos_promocoes_dell == 'Confirmar':
                        codigo = valores_promocoes_dell['cod']

                        cursor.execute("SELECT cod_produtos FROM promocao WHERE cod_produtos = %s;", (codigo,))
                        linha = cursor.fetchone()

                        if linha is not None:                            
                            cursor.execute("DELETE FROM promocao WHERE cod_produtos = %s;", (codigo,))
                            banco.commit()
                            sg.popup("Promoção Deletada com Sucesso!")  
                            janela_promocoes_dell.close()  
                        else: 
                            sg.popup("A promoção não pode ser deletada, pois não existe!")
                            janela_promocoes_dell.close()
                    elif eventos_promocoes_dell == 'Voltar':
                        janela_promocoes_dell.close()
                
                        janela_promocoes_dell.close()
            elif eventos_promocoes == 'Voltar':
                janela_promocoes.close()

                janela_promocoes.close()

cursor.close()
banco.close()
janela.close()