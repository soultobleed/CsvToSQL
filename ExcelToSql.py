# coding: utf-8
"""
A ideia eh pegar uma listagem em csv sendo:
a primeira linha o nome da tabela destino
a segunda linha uma listagem com os campos
e as demais linhas com os dados escapados para um insert direto

Inspirado em: http://tools.perceptus.ca/text-wiz.php?ops=7
"""
from __future__ import print_function

import csv
import os
import sys
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from escape_chars import escape


def trata_dados(string):
    """
    Retorna os dados de string escapados conforme a tabela em escape_chars
    Args:
        string: Uma string para ser traduzida
    """

    return string.translate(None, ''.join(escape))


def retorna_linha(nome_tabela, campos, dados_linha):
    sql_string = """INSERT INTO %s""" % nome_tabela
    sql_string += " ("
    sql_string += ', '.join(campos)
    sql_string += """) VALUES ("""
    for d in dados_linha:
        sql_string += "'" + trata_dados(d) + "',"
    sql_string = sql_string[:-1]
    sql_string += ");"
    return sql_string


def obtem_dialeto(data):
    """
    Tenta obter o dialeto do arquivo csv
    Wrapper para o metodo csv.Sniffer().sniff

    Args:
        data: Algumas linhas de exemplo do arquivo original
    Returns:
        Um objeto csv.Dialect
    """
    
    return csv.Sniffer().sniff(data)


def retorna_resultado(arquivo, saida=sys.stdout):
    """
    Escreve os dados formatados de "arquivo" em um formato para insert em banco de dados

    Args:
        arquivo: local do arquivo
        saida: arquivo de saida
    """
    fp = StringIO.StringIO()
    fp.writelines(open(arquivo, 'rb').readlines())
    # fileobj = open(arquivo, 'r+')
    # fp = mmap.mmap(fileobj.fileno(), 0)
    fp.seek(0)
    linha = 1
    nome_tabela = ''
    campos = list()
    dados = list()
    arquivo_valido = os.path.isfile(arquivo)
    ret = list()
    
    if not arquivo_valido:
        raise IOError('Arquivo não é válido: %s' % arquivo)

    # TODO: Possibilitar o uso de um arquivo em formato Excel
    fp.readline() # Pular a primeira linha para desconsiderar o nome da tabela
    # Lendo ate 8192 bytes, para o metodo sniff sao necessarias algumas linhas de exemplo
    first_bytes = fp.read(8192)
    dialect = obtem_dialeto(first_bytes)
    arq = csv.reader(fp, dialect=dialect)
    fp.seek(0)  # Retorna ao começo do arquivo após descobrir o dialeto
    for L in arq:
            if linha == 1:  # O primeiro campo deveria ser o nome da tabela
                nome_tabela = L[0]
            elif linha == 2:  # O segundo campo deveriam ser os campos para o insert
                campos = L
            elif linha >= 3:
                ret += retorna_linha(nome_tabela=nome_tabela, campos=campos, dados_linha=L)
            linha += 1
    with open(saida, 'w') as arq_ret:
        arq_ret.writelines(ret)
   
    
def main():
    # TODO: Possibilitar criar a tabela a partir da linha de comando
    # TODO: Permitir a exportação para arquivo de texto sem redirecionar a saída
    arquivo = os.path.abspath(sys.argv[1])
    arquivo_saida = None
    if len(sys.argv) == 3:
        arquivo_saida = 'output.sql'
    retorna_resultado(arquivo, saida=arquivo_saida)

if __name__ == '__main__':
    main()
