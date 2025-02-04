import re
from datetime import date

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