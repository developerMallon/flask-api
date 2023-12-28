import os
import requests
import pandas as pd
from app.services.employees_info import employee_info_mapping
from dotenv import dotenv_values

# Carrega os valores do .env
config = dotenv_values(".env")

API_URL = config["API_URL"]
API_KEY = config["API_KEY"]

# Cabeçalhos (headers) que você deseja enviar na requisição
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}',
}


def getMetas(dtInicial, dtFinal):
    # Corpo para consulta das METAS
    dataMetas = {
        "idrelatorioconfiguracao": 320,
        "idrelatorioconsulta": 154,
        "idrelatorioconfiguracaoleiaute": 320,
        "idrelatoriousuarioleiaute": 175,
        "ididioma": 1,
        "listaempresas": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "filtros": f"DataMovimentoInicial=${dtInicial};  DataMovimentoFinal=${dtFinal}; TipoMovimentoUsuario=null; TipoMercadoria=null; ModeloVeiculo=null; TipoVendaVeiculo=null; TipoOS=null; TipoServico=null; CodigoPessoa=null; GrupoPessoa=null; TipoMeta=4,5; TipoAtividade=null"
    }

    # METAS - Faz a requisição POST com os cabeçalhos e dados especificados
    response = requests.post(API_URL, headers=headers, json=dataMetas)

    if response.status_code == 200:
        # Converte a resposta JSON em um DataFrame do Pandas
        data_json = response.json()
        df_metas = pd.DataFrame(data_json)

        # Lista de "PessoaVendedor" que você deseja excluir
        pessoas_a_excluir = ["MALLON CONCESSIONARIA DE VEICULOS COMERCIAIS LTDA",
                             "JOAO VITOR AMANCIO DE OLIVEIRA", "SAMUEL DVOJATZKI"]

        # Adiciona uma coluna definindo se o CANAL de Vendas e a Filial ou GA/MTS
        # ====================================================================
        def define_emp(row):
            # Importa as definições dos colaboradores do employees_info.py
            colaborador_info = employee_info_mapping.get(row['nomepessoa'])

            if colaborador_info:
                return colaborador_info['filial'], colaborador_info['canal']
            else:
                return row['empresa'], None

        df_metas[['filial', 'canal']
                 ] = df_metas.apply(define_emp, axis=1, result_type='expand')
        # ====================================================================

        # Cria um novo DataFrame excluindo as linhas com os "PessoaVendedor" especificados
        df_metas = df_metas.loc[~df_metas['nomepessoa'].isin(
            pessoas_a_excluir)]
        # Adiciona os campos 'vendedor' e 'empresa' pra fica igual nos 3 df
        df_metas['vendedor'] = df_metas['nomepessoa']

        # Adiciona o campo tipo para reduzir a descrição do tipometa (pega apenas a ultima palavra MERCADORIAS ou SERVIÇOS)
        df_metas['tipo'] = df_metas['tipometa'].str.split().str[-1]

        # Converte o campo "anomes" do dataset METAS de string para datetime
        df_metas["anomes"] = pd.to_datetime(df_metas['anomes'], format="mixed")

        # Adiciona no data frame METAS a coluna "Month" formada pelo ANO e o MES da coluna "anomes"
        df_metas["Month"] = df_metas["anomes"].dt.strftime('%Y-%m')
        df_metas["Day"] = df_metas["anomes"].dt.strftime('%d')

        return df_metas
    else:
        # return response.status_code, response.text
        return None


def getMercadorias(dtInicial, dtFinal):
    # Corpo para consulta das VENDAS
    dataVendas = {
        "idrelatorioconfiguracao": 138,
        "idrelatorioconsulta": 55,
        "idrelatorioconfiguracaoleiaute": 138,
        "idrelatoriousuarioleiaute": 216,
        "ididioma": 1,
        "listaempresas": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "filtros": f"IntermediacaoMarketplace=null; TipoMovimentoInterno=1,3,4,5,6,8,9,11,14,15,16,17,28,29,30,31,32,33,34,33,34,35,36,18,21,22,23,24,25,26,27,44; Consultor=null; MarcaMercadoria=null; TipoOperacao=null; CodigoMercadoria=null; Estoquista=null; MarcaVeiculo=null; TipoVeiculo=null; ModeloVeiculo=null; DataMovimentacaoInicial={dtInicial}; Pessoa=null; Vendedor=null; TributacaoEstadual=null; TipoMovimentoUsuario=16,418,17,257,228,286,18,504,461,67,407,68,275,246,304,69,493,450,25,406,26,276,247,305,27,492,449,37,391,38,264,235,293,39,477,434,40,402,41,249,220,278,42,488,445,379,381,382,380,383,394,384,480,437,385,387,388,386,389,393,390,479,436,55,425,56,265,236,294,57,511,468,31,426,32,266,237,295,33,512,469,646,647,648,649,650,651,652,653,654,637,638,639,640,641,642,643,644,645,601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,624,625,626,627,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,628,629,630,631,632,633,634,635,636,28,397,29,251,222,280,30,483,440,373,378,375,374,376,395,377,481,438,538,543,545,546,541,540,544,542,539,58,392,59,252,223,281,60,478,435,34,428,35,268,239,297,36,514,471,361,366,399,365,364,362,363,485,442,217,401,219,277,248,306,218,487,444; Gerarsaldos=False; DataMovimentacaoFinal={dtFinal}; RegimeMonofasico=null; TipoMercadoria=null; TipoLocalizacao=null"
    }

  # METAS - Faz a requisição POST com os cabeçalhos e dados especificados
    response = requests.post(API_URL, headers=headers, json=dataVendas)

    if response.status_code == 200:
        # Converte a resposta JSON em um DataFrame do Pandas
        data_json = response.json()
        df_mercadorias = pd.DataFrame(data_json)

        # Converte o campo "datamovimentacao" do dataset MERCADORIAS de string para datetime
        df_mercadorias["datamovimentacao"] = pd.to_datetime(
            df_mercadorias['datamovimentacao'], format="mixed")
        # Adiciona os campos 'vendedor' e 'empresa' pra fica igual nos 3 df
        # df_mercadorias['vendedor'] = df_mercadorias['pessoavendedor']
        df_mercadorias['vendedor'] = df_mercadorias.apply(lambda row: row['pessoaconsultor'] if pd.notna(
            row['pessoaconsultor']) else row['pessoavendedor'], axis=1)

        # Adiciona uma coluna definindo se o CANAL de Vendas e a Filial ou GA/MTS
        # ====================================================================
        def define_emp(row):
            # Importa as definições dos colaboradores do employees_info.py
            colaborador_info = employee_info_mapping.get(row['vendedor'])

            if colaborador_info:
                return colaborador_info['filial'], colaborador_info['canal']
            else:
                return row['empresareduzida'], None

        df_mercadorias[['filial', 'canal']
                       ] = df_mercadorias.apply(define_emp, axis=1, result_type='expand')
        # ====================================================================

        # Adiciona uma coluna chamada 'totalmercadoria' para ficar igual ao 'df_servicos' e facilitar a soma de vendas de mercadorias
        df_mercadorias['totalmercadoria'] = df_mercadorias['valortotal']
        # df_mercadorias["Month"] = df_mercadorias["datamovimentacao"].apply(lambda x: str(x.year) + "-" + str(x.month))
        df_mercadorias["Month"] = df_mercadorias["datamovimentacao"].dt.strftime(
            '%Y-%m')
        df_mercadorias["Day"] = df_mercadorias["datamovimentacao"].dt.strftime(
            '%d')

        return df_mercadorias
    else:
        # return response.status_code, response.text
        return None


def getServicos(dtInicial, dtFinal):
    # Corpo para consulta de SERVICOS
    dataServicos = {
        "idrelatorioconfiguracao": 393,
        "idrelatorioconsulta": 95,
        "idrelatorioconfiguracaoleiaute": 393,
        "idrelatoriousuarioleiaute": 184,
        "ididioma": 1,
        "listaempresas": [2, 3, 4, 5, 6],
        "filtros": f"ConsiderarTecnico=True; FontePagadora=null; Segmento=null; SomenteManutencaoFrotista=False; IdsMercadorias=null; SituacaoConcluidaNF=null; NomeEmissaoDocumento=null; TipoBaixaDocumento=null; TipoOrdemServicoInterno=null; EstadoVeiculo=null; TipoRecepcao=null; ItensServicosCancelados=False; EquipeAtendimentoFrotista=null; NumeroContratoFrotista=; TipoVeiculoOS=null; ConsultorFechamento=null; OSSituacao=null; VeiculoCliente=null; AnoInicial=0; AnoFinal=999999999; IdsServicos=null; Tiposervico=null; Municipio=null; Tecnico=null; Modelo=null; Pessoa=null; Tipodeordemdeservico=null; Consultor=null; NumeroOS=null; Periododeconclusaoinicial={dtInicial}; Periododeconclusaofinal={dtFinal}; Tipoitem=3,1,4,2; TipoMovimentoMercadoria=null; TipoDeVeiculoModelo=null"
    }

    # Faz a requisição POST com os cabeçalhos e dados especificados
    response = requests.post(API_URL, headers=headers, json=dataServicos)
    # response = requests.get("https://www.google.com.br")

    if response.status_code == 200:
        # Converte a resposta JSON em um DataFrame do Pandas
        data_json = response.json()
        df_servicos = pd.DataFrame(data_json)

        # Converte o campo "datahorabaixa" do dataset SERVICOS de string para datetime
        df_servicos["datahorabaixa"] = pd.to_datetime(
            df_servicos['datahorabaixa'], format="mixed")

        # Adiciona os campos 'vendedor' e 'empresa' pra fica igual nos 3 df
        df_servicos['vendedor'] = df_servicos['pessoaconsultor']

        # ====================================================================
        def define_emp(row):
            # Importa as definições dos colaboradores do employees_info.py
            colaborador_info = employee_info_mapping.get(row['pessoaconsultor'])

            if colaborador_info:
                return colaborador_info['filial'], colaborador_info['canal']
            else:
                return row['empresa'], None

        df_servicos[['filial', 'canal']
                    ] = df_servicos.apply(define_emp, axis=1, result_type='expand')
        # ====================================================================

        df_servicos["servico_e_cortesia"] = df_servicos["totalservico"] + df_servicos["totalcortesia"]

        # Adiciona no dataframe SERVICOS a coluna "Month" formada pelo ANO e o MES da coluna "datahorabaixa"
        df_servicos["Month"] = df_servicos["datahorabaixa"].dt.strftime('%Y-%m')

        return df_servicos
    else:
        # return response.status_code, response.text
        return None
