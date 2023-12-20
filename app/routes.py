from app import app
from flask import Flask, request, jsonify, abort
import jwt
from dotenv import dotenv_values
import pandas as pd
from functools import wraps
from app.services.calc_days import calcDays
from app.services.holidays import holidays
from app.services.getDatesInOut import getDatesInOut
from app.services.employees_info import employee_info_mapping
from app.api.api import getMetas, getMercadorias, getServicos

# Carrega os valores do .env
config = dotenv_values(".env")

# Decorator para validar o token
def verify_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Obtém o token do cabeçalho Authorization
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return 'Token não fornecido', 401

        # Verifica se o cabeçalho começa com 'Bearer '
        if not authorization_header.startswith('Bearer '):
            return 'Formato de token inválido', 401

        # Extrai o token removendo 'Bearer ' do início
        token = authorization_header.split(' ')[1]

        if token:
            try:
                payload = jwt.decode(
                    token, config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return 'Token expirado. Faça login novamente.', 401
            except jwt.InvalidTokenError:
                return 'Token inválido. Faça login novamente.', 401

        return f(*args, **kwargs)

    return wrapper

@app.route('/')
def index():
    resultado = {
        "message": "Api flask rodando."
    }
    return jsonify(resultado), 200

@app.route('/token', methods=['POST'])
@verify_token
def token():
    resultado = {
        "message": "Token validado com sucesso."
    }
    return jsonify(resultado), 200

@app.route('/dias-uteis/<mes>/<ano>/<filial>', methods=['POST'])
@verify_token
def dias_uteis(mes, ano, filial):
    
    dias_uteis, dias_passados = calcDays(int(mes), int(ano), holidays[filial])

    # Cria um dicionário com os resultados
    resultado = {
        "dias-uteis":  {
            'total': dias_uteis,
            'passados': dias_passados,
            'restantes': dias_uteis - dias_passados
        }
    }
    
    # Retorna a resposta no formato JSON
    return jsonify(resultado), 200

@app.route('/resumo-vendas/<mes>/<ano>/<filial>', methods=['POST'])
@verify_token
def resumo(mes, ano, filial):

    dtInicial, dtFinal = getDatesInOut()

        # ================================ Carregando os dataframes ================================
    df_metas = getMetas(dtInicial, dtFinal)
    df_mercadorias = getMercadorias(dtInicial, dtFinal)
    df_servicos = getServicos(dtInicial, dtFinal)

    # ==================================== Verifica se houve erro na resposta da API ====================================
    if df_metas is None:
        abort(404, "A resposta da API/Metas não é um DataFrame válido")

    if df_mercadorias is None:
        abort(404, "A resposta da API/Mercadorias não é um DataFrame válido")

    if df_servicos is None:
        abort(404, "A resposta da API/Serviços não é um DataFrame válido")

    # ===================================== Concatena todos os vendedores da empresa ====================================
    vendedores = []
    consultores = []

    for nome, info in employee_info_mapping.items():
        if info["canal"] == "balcao":
            vendedores.append(nome)
        elif info["canal"] == "oficina":
            consultores.append(nome)

    # ================================== CALCULA E ORGANIZA AS INFORMAÇÃO NO DF_FINAL ===================================
    # Metas de MERCADORIAS por filial
    df_metas = df_metas[df_metas['vendedor'].isin(vendedores + consultores)]
    df_metas_mercadorias = df_metas[df_metas['tipo'] == "MERCADORIAS"]
    df_metas_mercadorias = df_metas_mercadorias.groupby('filial')[
        'valormeta'].sum()

    # Metas de SERVIÇOS por filial
    df_metas = df_metas[df_metas['vendedor'].isin(vendedores + consultores)]
    df_metas_servicos = df_metas[df_metas['tipo'] == "SERVIÇOS"]
    df_metas_servicos = df_metas_servicos.groupby('filial')['valormeta'].sum()

    # Aqui precisa filtrar para não aparecerem os ESTOQUISTA/GARANTISTAS
    df_mercadorias = df_mercadorias[df_mercadorias['vendedor'].isin(
        vendedores + consultores)]

    # Vendas de mercadorias por filial
    df_mercadorias_filial = df_mercadorias.groupby(
        'filial')['totalmercadoria'].sum()

    # Junta os DataFrames METAS e MERCADORIAS com base na coluna "empresa"
    df_mercadorias_final = pd.merge(
        df_metas_mercadorias, df_mercadorias_filial, on='filial')
    perc = df_mercadorias_final['totalmercadoria'] / \
        df_mercadorias_final['valormeta'] * 100
    df_mercadorias_final["percentagePecas"] = perc.round(2)

    # Aqui precisa filtrar para não aparecerem os ESTOQUISTA/GARANTISTAS
    df_servicos = df_servicos[df_servicos['vendedor'].isin(
        vendedores + consultores)]

    # Vendas de serviços/MO por filial
    df_servicos_filial = df_servicos.groupby('filial')['servico_e_cortesia'].sum()

    # Junta os DataFrames METAS e SERVIÇOS com base na coluna "empresa"
    df_servicos_final = pd.merge(
        df_metas_servicos, df_servicos_filial, on='filial')
    perc = df_servicos_final['servico_e_cortesia'] / \
        df_servicos_final['valormeta'] * 100
    df_servicos_final["percentageServicos"] = perc.round(2)

    # Junta as informações de METAS e VENDAS de MERCADORIAS e SERVIÇOS
    df_final = pd.merge(df_mercadorias_final, df_servicos_final, on='filial')
    df_final["metaPSC"] = df_final["valormeta_x"] + df_final["valormeta_y"]
    df_final["vendidoPSC"] = df_final["totalmercadoria"] + \
        df_final["servico_e_cortesia"]
    perc = df_final["vendidoPSC"] / df_final["metaPSC"] * 100
    df_final["percentagePSC"] = perc.round(2)
    df_final = df_final.reset_index()

    # # Ordenar e renomear as colunas para ficar igual planilha
    # df_final = df_final[["empresa", "valormeta_x", "totalmercadoria", "%Peças",
    #                      "valormeta_y", "servico_e_cortesia", "%Serviços", "PSC Meta", "PSC Realizado"]]
    df_final = df_final.rename(
        columns={
            'filial': 'filial',
            'totalmercadoria': 'vendidoPecas',
            'valormeta_x': 'metaPecas',
            'servico_e_cortesia': 'vendidoServicos',
            'valormeta_y': 'metaServicos',
        })

    # Cria função que irá formatar os números
    def formatar(valor):
        valor_formatado = "{:,.2f}".format(valor)
        valor_formatado = valor_formatado.replace(',', '_')
        valor_formatado = valor_formatado.replace('.', ',')
        valor_formatado = valor_formatado.replace('_', '.')

        return valor_formatado

    # Aplica a formatação para as colunas desejadas
    colunas_para_formatar = ["metaPecas", "vendidoPecas", "percentagePecas",
                            "metaServicos", "vendidoServicos", "percentageServicos", "metaPSC", "vendidoPSC", "percentagePSC"]
    for coluna in colunas_para_formatar:
        df_final[coluna] = df_final[coluna].apply(formatar)

    # Converte o DataFrame para um dicionário
    dados_formatados = df_final.to_dict(orient='records')

    return jsonify(dados_formatados)
    