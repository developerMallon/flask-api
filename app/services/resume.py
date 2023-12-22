import pandas as pd
from datetime import datetime
from flask import flash, session
from app.api.api import getMetas, getMercadorias, getServicos
from services.holidays import holidays
from services.calc_days import calcDays
from services.getDatesInOut import getDatesInOut
from services.employees_info import employee_info_mapping
from pylocalstorage import LocalStorage

ls = LocalStorage()

# Verifica se o MÊS SELECIONADO existe, caso não ele seta com o valor do mês corrente
selected_month = ls.getItem('selected_month')
if not selected_month:
    ls.setItem('selected_month',datetime.now().strftime('%Y-%m'))

# Define a data inicial e final do período avaliado
# Se não passar o mês e o ano para função getDatesInOut retorno do mês atual
# getDatesInOut(month, year)
dtInicial, dtFinal = getDatesInOut(selected_month)

# Com base na data inicial retorna os dias úteis e os dias passados até o momento
date_object = datetime.strptime(dtInicial, "%Y-%m-%d")
dias_uteis, dias_passados = calcDays(date_object.month, date_object.year, holidays['mafra'])

def df_dias_uteis():
    df_dias = pd.DataFrame({
        "Dias Úteis": [dias_uteis], 
        "Dias Passados": [dias_passados],
        "Dias Restantes": [dias_uteis - dias_passados],
    })

    return df_dias

# ================================ Carregando os dataframes ================================
df_metas = getMetas(dtInicial, dtFinal)
df_mercadorias = getMercadorias(dtInicial, dtFinal)
df_servicos = getServicos(dtInicial, dtFinal)

# ==================================== Verifica se houve erro na resposta da API ====================================
if df_metas is None:
    flash("A resposta da API/Metas não é um DataFrame válido")
    raise ValueError(
        "Resposta API com valor nulo encontrado. O programa será encerrado.")

if df_mercadorias is None:
    flash("A resposta da API/Mercadorias não é um DataFrame válido")
    raise ValueError(
        "Resposta API com valor nulo encontrado. O programa será encerrado.")

if df_servicos is None:
    flash("A resposta da API/Serviços não é um DataFrame válido")
    raise ValueError(
        "Resposta API com valor nulo encontrado. O programa será encerrado.")

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
df_mercadorias_final["% Peças"] = perc.round(2)

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
df_servicos_final["% Serviços"] = perc.round(2)

# Junta as informações de METAS e VENDAS de MERCADORIAS e SERVIÇOS
df_final = pd.merge(df_mercadorias_final, df_servicos_final, on='filial')
df_final["Meta PSC"] = df_final["valormeta_x"] + df_final["valormeta_y"]
df_final["R$ PSC"] = df_final["totalmercadoria"] + \
    df_final["servico_e_cortesia"]
perc = df_final["R$ PSC"] / df_final["Meta PSC"] * 100
df_final["% PSC"] = perc.round(2)
df_final = df_final.reset_index()

# # Ordenar e renomear as colunas para ficar igual planilha
# df_final = df_final[["empresa", "valormeta_x", "totalmercadoria", "%Peças",
#                      "valormeta_y", "servico_e_cortesia", "%Serviços", "PSC Meta", "PSC Realizado"]]
df_final = df_final.rename(
    columns={
        'filial': 'Filial',
        'totalmercadoria': 'R$ Peças',
        'valormeta_x': 'Meta Peças',
        'servico_e_cortesia': 'R$ Serviços',
        'valormeta_y': 'Meta Serviços',
    })

# Cria função que irá formatar os números
def formatar(valor):
    valor_formatado = "{:,.2f}".format(valor)
    valor_formatado = valor_formatado.replace(',', '_')
    valor_formatado = valor_formatado.replace('.', ',')
    valor_formatado = valor_formatado.replace('_', '.')

    return valor_formatado

df_final["Meta Peças"] = df_final["Meta Peças"].apply(formatar)
df_final["R$ Peças"] = df_final["R$ Peças"].apply(formatar)
df_final["% Peças"] = df_final["% Peças"].apply(formatar)
df_final["Meta Serviços"] = df_final["Meta Serviços"].apply(formatar)
df_final["R$ Serviços"] = df_final["R$ Serviços"].apply(formatar)
df_final["% Serviços"] = df_final["% Serviços"].apply(formatar)
df_final["Meta PSC"] = df_final["Meta PSC"].apply(formatar)
df_final["R$ PSC"] = df_final["R$ PSC"].apply(formatar)
df_final["% PSC"] = df_final["% PSC"].apply(formatar)

def df_resumo():
    return df_final
