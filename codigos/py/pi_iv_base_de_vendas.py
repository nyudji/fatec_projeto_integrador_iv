# -*- coding: utf-8 -*-
"""PI IV Base de Vendas.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1N9NmCcaJ3HH1Ynj18Db8qRJKuK7WDQxP

## Projeto Integrador 4 Base de Vendas

Projeto tem a bases de vendas de e-commerces ou lojas físicas, que serão estruturadas para um data lake e depois um datawarehouse. Usando técnicas cloud(GCP)

#### Instalações de Ferramentas/Bibliotecas necessárias
"""

!pip install google-cloud-bigquery

from google.colab import auth
auth.authenticate_user()
from google.cloud import bigquery
from google.cloud import storage
import pandas as pd
from datetime import datetime
import zipfile
import os
import numpy as np

"""#### Importando arquivos csv pro colab"""

# Define os caminhos dos arquivos zipados
zip_file_paths = ['/content/Bases/archive.zip']  # Substitua pelos nomes dos seus arquivos ZIP

# Função para extrair um arquivo ZIP
def extract_zip(zip_path, extract_to='/content/Bases/'):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Extrai cada arquivo ZIP
for zip_file_path in zip_file_paths:
    extract_zip(zip_file_path)

# Verifica o conteúdo do diretório para garantir que os arquivos foram extraídos
os.listdir('/content/Bases/')

"""#### Conexão

Com GCP
"""

#client = storage.Client()
#bucket = client.bucket('datalake_vendas')
#df_vendas = pd.read_csv('gs://datalake_vendas/dados_brutos/data.csv', encoding='latin-1')

"""Com Arquivo local Colab"""

df_vendas = pd.read_csv('/content/Bases/data.csv', encoding='latin-1')

"""### Trabalhando com a base E-Commerce (data.csv)

Mostrando DF do pandas que importamos da GCS
"""

df_vendas

df_vendas.info()

"""#### Tratamento da base

Tirando os que tem os preços = 0 e campos nulls

---
"""

df_vendas_tratado = df_vendas[df_vendas.notnull().all(axis=1) & (df_vendas['UnitPrice'] != 0) & (df_vendas['Quantity'] != 0)]

#Visualização
df_vendas_tratado.head(1)

colunas_dropadas = ['CustomerID', 'Country']

# Para dropar várias colunas, passe a lista de nomes das colunas e especifique o eixo (axis=1)
df_vendas_tratado = df_vendas_tratado.drop(colunas_dropadas, axis=1)

"""Renomeando e estruturando a base"""

novos_nomes = {'InvoiceNo': 'Cod_Fatura', 'StockCode': 'Cod_Estoque', 'Description': 'Produto', 'Quantity':'Quantidade','InvoiceDate':'Data','UnitPrice':'Preco_Unitario'}
df_vendas_tratado = df_vendas_tratado.rename(columns=novos_nomes)

# Exibir o DataFrame com as colunas renomeadas
df_vendas_tratado.head(1)

"""Estruturando"""

# Definir a nova ordem das colunas
nova_ordem = ['Cod_Fatura', 'Cod_Estoque', 'Produto', 'Quantidade','Preco_Unitario','Data']

# Reordenar as colunas do DataFrame
df_vendas_tratado = df_vendas_tratado[nova_ordem]

"""Tratamento dtypes"""

#Transformando Numericos
df_vendas_tratado['Cod_Fatura'] = df_vendas_tratado['Cod_Fatura'].astype(str)
df_vendas_tratado['Preco_Unitario'] = df_vendas_tratado['Preco_Unitario'].astype(float)
#Convertendo a coluna para string
df_vendas_tratado['Produto'] = df_vendas_tratado['Produto'].astype(str)

"""Dropando coluna Cod_Estoque"""

df_vendas_tratado.drop('Cod_Estoque', axis=1, inplace=True)

"""Colocando Total Fatura com Quantidade * Preco_Unitario"""

df_vendas_tratado['Fatura_Total'] = df_vendas_tratado['Quantidade'] * df_vendas_tratado['Preco_Unitario']

"""Deixa Total Fatura com apenas dois decimais"""

df_vendas_tratado['Fatura_Total'] = df_vendas_tratado['Fatura_Total'].round(2)

"""Colocando data no formato (DIA/MES/ANO H:M)"""

df_vendas_tratado['Data'] = pd.to_datetime(df_vendas_tratado['Data'])

df_vendas_tratado['Data'] = df_vendas_tratado['Data'].dt.strftime('%d/%m/%Y %H:%M')

"""Tirando dados com quantidade negativa"""

df_vendas_tratado = df_vendas_tratado[df_vendas_tratado['Quantidade'] >= 0]

df_vendas_tratado.info()

"""Visualização Final"""

df_vendas_tratado

"""Importando CSV para GCS"""

'''from google.colab import auth
auth.authenticate_user()

# Monte o bucket do GCS
from google.cloud import storage
client = storage.Client()
bucket = client.bucket('datalake_vendas')


# Escreva os dados de volta para o GCS
df_vendas_tratado.to_csv('gs://datalake_vendas/dados_tratados/data_tratado.csv',index=False)

"""Importando para disco local"""

df_vendas_tratado.to_csv('/content/Bases/data_tratado.csv',index=False)

"""Exportando para o Big Query"""

'''from google.cloud import bigquery
import pandas as pd

# ID do projeto
id_projeto = 'ID_PROJETO_GCP

# Crie um cliente BigQuery com o ID do projeto
client = bigquery.Client(project=id_projeto)

# Escolha o nome da tabela permanente no BigQuery
nome_tabela = 'tb_vendas'

# Salve o DataFrame Pandas na tabela permanente no BigQuery (anexar dados)
tabela_ref = client.dataset('db_vendas').table(nome_tabela)
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Adiciona os dados à tabela existente
)
job = client.load_table_from_dataframe(df_vendas_tratado, tabela_ref, job_config=job_config)
job.result()  # Aguarda a conclusão do carregamento

print(f'DataFrame tratado adicionado à tabela {nome_tabela} no BigQuery.')

"""Importando do Big Query"""

''''from google.cloud import bigquery

#ID DO PROJETO
id_projeto = 'ID_PROJETO_GCP'

#Crie um cliente BigQuery com o ID do projeto
client = bigquery.Client(project=id_projeto)

# Escolha um conjunto de dados (substitua "db_vendas" pelo nome do seu conjunto de dados)
dataset_ref = client.dataset('db_vendas')

# Escolha uma tabela (substitua "tb_vendas" pelo nome da sua tabela)
tabela_vendas = dataset_ref.table('tb_vendas')

# Carregue a tabela em um DataFrame do Pandas
tabela = client.get_table(tabela_vendas)
df_vendas_dw = client.list_rows(tabela).to_dataframe()

df_vendas_dw.head(1)

"""### Testes API

Teste com a Random API para trazer mais faturas , salvas no GCS como dados gerados e tratados , utilizando js na parte da randomapi e python na parte do Cloud Functions
"""

'''import requests


url = 'https://randomapi.com/api/z8zovuyu?key=M8R0-L7CV-HYYP-XWDI'
response = requests.get(url)
data = response.json()
results = data.get('results')
df_vendas_random = pd.DataFrame(results)
df_vendas_random

#Renomeando colunas
'''novos_nomes = {'invoiceID': 'Cod_Fatura', 'date': 'Data', 'items': 'Produto', 'itemsPurchased':'Quantidade','price':'Preco_Unitario','card':'Cartao','country':'Pais'}
df_vendas_random = df_vendas_random.rename(columns=novos_nomes)

# Definir a nova ordem das colunas
nova_ordem = ['Cod_Fatura', 'Produto', 'Quantidade','Preco_Unitario','Data','Pais','Cartao']

# Reordenar as colunas do DataFrame
'''df_vendas_random = df_vendas_random[nova_ordem]

#Dropando coluna cartao
'''df_vendas_random.drop('Cartao', axis=1, inplace=True)

'''df_vendas_random.info()

#Arrumando o formato da Data
'''df_vendas_random['Data'] = pd.to_datetime(df_vendas_random['Data']).dt.strftime('%m/%d/%Y %H:%M')

#Transformando Numericos
'''df_vendas_random['Cod_Fatura'] = df_vendas_random['Cod_Fatura'].astype(str)
df_vendas_random['Preco_Unitario'] = df_vendas_random['Preco_Unitario'].astype(float)

#Convertendo a coluna para string
'''df_vendas_random['Produto'] = df_vendas_random['Produto'].astype(str)

'''df_vendas_random.head(1)

'''#Colocando no datalake
bucket_name = 'datalake_vendas'
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)
filename = f'dados_random_tratados.csv'

# Verifica se já existe um arquivo com este nome
blob = bucket.blob('dados_tratados/' + filename)
if blob.exists():
            # Se o arquivo já existir, recupera o DataFrame existente
      existing_df = pd.read_csv(f"gs://{bucket_name}/dados_tratados/{filename}")

            # Concatena o novo DataFrame com o existente
      df_vendas_random = pd.concat([existing_df, df_vendas_random])

        # Salva o DataFrame como CSV no bucket
df_vendas_random.to_csv(f"gs://{bucket_name}/dados_tratados/{filename}", index=False)

"""### Base Licores

#### Parte Pyspark
"""

#!pip install google-cloud-storage pyspark

'''from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import requests

# Inicializa a sessão Spark
spark = SparkSession.builder.appName("GetCountryFromLocation").getOrCreate()

# Sua chave API do Google Maps
api_key = "AIzaSyBoXN9Lsinv4_DVDR4hXfRJ7-9ZCXMkats"  # Substitua por sua chave API

# Função UDF para obter o país a partir das coordenadas
import requests

def get_country(location):
    try:
        # Extrai a latitude e longitude da coluna 'location'
        longitude, latitude = map(float, location.strip('POINT ()').split())

        # URL da API do Google Maps para geocodificação reversa
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"

        # Faz uma solicitação à API
        response = requests.get(url)

        # Verifica se a solicitação foi bem-sucedida
        if response.status_code == 200:
            # Analisa a resposta JSON
            data = response.json()

            # Verifica se há resultados
            if data.get('results'):
                # Itera pelos resultados para encontrar o país
                for result in data['results']:
                    # Itera pelos componentes de endereço para encontrar o país
                    for component in result.get('address_components', []):
                        if 'country' in component['types']:
                            return component['long_name']

            # Se não encontrou o país nos resultados
            return "País não encontrado"
        else:
            # Se a solicitação falhou
            return "Erro na solicitação à API"
    except Exception as e:
        # Se ocorreu algum erro durante o processamento
        return f"Erro ao processar a localização: {str(e)}"


# Define a UDF
get_country_udf = udf(get_country, StringType())

# Carrega seus dados
df = spark.createDataFrame(
    [
        ("POINT (-93.597011 41.570844)",),
        ("POINT (-43.209375 -22.908448)",),
    ],
    ["location"]
)

# Aplica a UDF à coluna 'location'
df = df.withColumn("country", get_country_udf(df["location"]))

# Exibe o DataFrame resultante
df.show(1)
spark.stop()

"""Tratamento pyspark Licor, rodado no Dataproc"""

'''from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from google.cloud import storage
from pyspark.sql.functions import col, udf
import os
import pandas as pd
from google.cloud import bigquery

# Inicializar cliente do Google Cloud Storage
storage_client = storage.Client()

# Inicializar SparkSession
spark = SparkSession.builder.appName("ETL-licores-orders").getOrCreate()



# Ler o arquivo CSV local
gcs_path = "gs://datalake_vendas/dados_brutos/Liquor_Sales.csv"


# Ler o arquivo CSV do GCS
df_liquor = spark.read.format("csv") \
    .option("header", "true") \
    .load(gcs_path)

# Remove linhas com valores nulos
df_liquor = df_liquor.na.drop()

#Filtra as que tem quantidade negativa
df_liquor = df_liquor.filter(col("Bottles Sold") > 0)

#Filtra a quantidade de dados
df_liquor = df_liquor.limit(50000)


# Seleciona e renomeia as colunas desejadas
df_liquor = df_liquor.select(
    col("Invoice/Item Number").alias("Cod_Fatura"),
    col("Date").alias("Data"),
    col("Store Number").alias("Cod_Dist"),
    col("Item Description").alias("Produto"),
    col("State Bottle Retail").alias("Preco_Unitario"),
    col("Bottles Sold").alias("Quantidade"),
    col("Sale (Dollars)").alias("Fatura_Total")
)

# Ordena as colunas
df_liquor = df_liquor.orderBy(
    "Cod_Fatura",
    "Cod_Dist",
    "Produto",
    "Quantidade",
    "Preco_Unitario",
    "Data",
    "Fatura_Total"
)



# Exibe as primeiras 10 linhas do DataFrame
df_liquor.show(7)
df_liquor = df_liquor.coalesce(1)
# Escreve o DataFrame no GCS
output_path = "gs://datalake_vendas/dados_tratados/Liquor_Sales_Tratado"
temp = 'gs://temp_tb_vendas'
df_liquor.write.mode("append").option("header", "true").csv(output_path)

# ID do projeto
id_projeto = 'central-kit-422716-u9'

# Crie um cliente BigQuery com o ID do projeto
client = bigquery.Client(project=id_projeto)

# Escolha o nome da tabela permanente no BigQuery
nome_tabela = 'tb_vendas'

# Converter DataFrame Spark para DataFrame Pandas
df_liquor_pandas = df_liquor.toPandas()
df_liquor_pandas["Cod_Fatura"] = df_liquor_pandas["Cod_Fatura"].astype(str)
df_liquor_pandas['Produto'] = df_liquor_pandas['Produto'].astype(str)
df_liquor_pandas["Quantidade"] = df_liquor_pandas["Quantidade"].astype(int)
df_liquor_pandas['Preco_Unitario'] = df_liquor_pandas['Preco_Unitario'].astype(float)
df_liquor_pandas['Fatura_Total'] = df_liquor_pandas['Fatura_Total'].astype(float)
df_liquor_pandas['Data'] = pd.to_datetime(df_liquor_pandas['Data']).dt.strftime('%d/%m/%Y %H:%M')

# Salve o DataFrame Pandas na tabela permanente no BigQuery (anexar dados)
tabela_ref = client.dataset('db_vendas').table(nome_tabela)
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Adiciona os dados à tabela existente
)
job = client.load_table_from_dataframe(df_liquor_pandas, tabela_ref, job_config=job_config)
job.result()  # Aguarda a conclusão do carregamento


# Parar o SparkSession para liberar recursos
spark.stop()

"""#### Tratamento Licores Vendas

##### Trazendo dados do Kaggle
"""

!kaggle datasets download -d pigment/big-sales-data

import zipfile
import os

# Descompactar o arquivo ZIP
with zipfile.ZipFile('big-sales-data.zip', 'r') as zip_ref:
    zip_ref.extractall('big-sales-data')

# Listar os arquivos extraídos
os.listdir('big-sales-data')

"""##### Carrega a base para o pandas"""

import pandas as pd
from google.colab import drive
from google.cloud import storage

#Metodo GCP
# Inicializar cliente do Google Cloud Storage
#storage_client = storage.Client()

# Nome do bucket
#bucket_name = "nome_do_seu_bucket"

# Caminho para o arquivo CSV no seu bucket
#blob_path = "gs://datalake_vendas/dados_brutos/Liquor_Sales.csv"

#Caminho CSV LICORES
local_csv_path = "/content/big-sales-data/Sales_Data/Liquor_Sales.csv"

# Baixa o arquivo do bucket para o ambiente Colab
#bucket = storage_client.bucket(bucket_name)
#blob = bucket.blob(blob_path)
#blob.download_to_filename(local_csv_path)

# Define as colunas que serão utilizadas
columns = [
    "Invoice/Item Number",
    "Date",
    "Store Number",
    "Item Description",
    "State Bottle Retail",
    "Bottles Sold",
    "Sale (Dollars)"
]

# Carrega apenas as colunas desejadas do CSV
df_liquor= pd.read_csv(local_csv_path, usecols=columns)

df_liquor.head(3)

"""#### Começo Tratamento Base Licores Orders"""

# Remove linhas com valores nulos
df_liquor_ord = df_liquor.dropna(inplace=True)

# Filtra as linhas com quantidade de garrafas vendidas maior que zero
df_liquor_ord = df_liquor[df_liquor["Bottles Sold"] > 0]

# Limita o número de linhas para 50000 (como no código original)
df_liquor_ord = df_liquor_ord.sample(n=50000, random_state=1)

# Converta a coluna 'Data' para o formato desejado
df_liquor_ord['Date'] = pd.to_datetime(df_liquor_ord['Date']).dt.strftime('%d/%m/%Y %H:%M')

# Renomeia as colunas
df_liquor_ord.rename(columns={
    "Invoice/Item Number": "Fatura_Cod",
    "Date": "Data",
    "Item Description": "Produto",
    "State Bottle Retail": "Preco_Unitario",
    "Bottles Sold": "Quantidade",
    "Sale (Dollars)": "Fatura_Total"
}, inplace=True)

# Ordena as colunas
df_liquor_ord = df_liquor_ord[[
    "Fatura_Cod",
    "Produto",
    "Quantidade",
    "Preco_Unitario",
    "Fatura_Total",
    "Data"
]]

# Ordenar as linhas do DataFrame
df_liquor_ord.sort_values(by=[
    "Fatura_Cod",
    "Produto",
    "Quantidade",
    "Preco_Unitario",
    "Fatura_Total",
    "Data"
], inplace=True)

df_liquor_ord.head(1)

"""Gerando horarios aleatorios"""

mask = df_liquor_ord['Data'].str.endswith('00:00')

# Função para gerar horários aleatórios mantendo a data
def gerar_horario_aleatorio(data):
    hora = np.random.randint(0, 24)
    minuto = np.random.randint(0, 60)
    return f"{data[:-5]}{hora:02d}:{minuto:02d}"

# Aplicar a função para gerar horários aleatórios nas datas com hora 00:00
df_liquor_ord.loc[mask, 'Data'] = df_liquor_ord.loc[mask, 'Data'].apply(gerar_horario_aleatorio)

df_liquor_ord.head(1)

"""##### Salvando

"""

# Escreve o DataFrame tratado em um novo arquivo CSV
#output_path = "gs://datalake_vendas/dados_tratados/Liquor_Sales_Tratado.csv"

#Escreve o df para um diretorio o Colab
output_path = "/content/Bases/Liquor_Sales_Tratado.csv"
df_liquor_ord.to_csv(output_path, index=False)



# ID do projeto
#id_projeto = 'seu_id_projeto'

# Nome da tabela permanente no BigQuery
#nome_tabela = 'tb_vendas'

# Crie um cliente BigQuery com o ID do projeto
#client = bigquery.Client(project=id_projeto)

# Carregue o DataFrame Pandas para a tabela permanente no BigQuery (anexar dados)
#tabela_ref = client.dataset('db_vendas').table(nome_tabela)
#job_config = bigquery.LoadJobConfig(
#    write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Adiciona os dados à tabela existente
#)
#job = client.load_table_from_dataframe(df_liquor_ord, tabela_ref, job_config=job_config)
#job.result()  # Aguarda a conclusão do carregamento

"""#### Tratamento Licores Distribuidores

##### Carregando
"""

'''import pandas as pd
from google.colab import drive
from google.cloud import storage


# Inicializar cliente do Google Cloud Storage
#storage_client = storage.Client()


#Caminho CSV LICORES
local_csv_path = "/content/big-sales-data/Sales_Data/Liquor_Sales.csv"
# Define as colunas que serão utilizadas

columns = [
    "Invoice/Item Number",
    "Store Number",
    "Store Name",
    "Address",
    "City",
    "Store Location"
]

# Carrega apenas as colunas desejadas do CSV
df_liquor = pd.read_csv(local_csv_path, usecols=columns)

df_liquor.head(1)

"""##### Tratamento"""

'''# Extrair IDs únicos de df_liquor_ord
ids_para_filtrar = df_liquor_ord['Fatura_Cod'].tolist()

# Filtrar os distribuidores (df_liquor_dist) com base nos IDs das ordens
df_liquor_dist = df_liquor[df_liquor['Invoice/Item Number'].isin(ids_para_filtrar)]
df_liquor_dist.drop(columns=["Invoice/Item Number"], inplace=True)


# Renomeia as colunas
df_liquor_dist.rename(columns={
    "Store Number": "Dist_Cod",
    "Store Name": "Dist_Nome",
    "Address": "Dist_Endereco",
    "City": "Dist_Cidade",
    "Store Location": "Dist_Localizacao"
}, inplace=True)

# Ordena as colunas
df_liquor_dist.sort_values(by=[
    "Dist_Cod",
    "Dist_Nome",
    "Dist_Endereco",
    "Dist_Cidade",
    "Dist_Localizacao"
], inplace=True)

''''import requests
import pandas as pd

def get_country_geocode_xyz(location):
    try:
        # Verifica se a localização é uma string e não é nula
        if isinstance(location, str) and location.startswith("POINT"):
            longitude, latitude = map(float, location.strip('POINT ()').split())
            url = f"https://geocode.xyz/{latitude},{longitude}?geoit=json"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'country' in data:
                    return data['country']
                return "Country not found"
            else:
                raise ValueError(f"API request failed (status code {response.status_code})")
        else:
            return "Invalid location format"

    except requests.exceptions.RequestException as e:
        return f"HTTP request failed: {str(e)}"
    except Exception as e:
        return f"Error processing location: {str(e)}"

# Supondo que você tenha um DataFrame `df` com uma coluna `location`
# Aqui está um exemplo de como isso pode ser feito

# Exemplo de DataFrame
data = {
    'location': ["POINT (-92.455796 42.517182)", "POINT (2.294694 48.858093)",'POINT (-92.455796 42.517182)','']  # Nova York, Paris, None, número inválido
}
df9 = pd.DataFrame(data)

# Aplicar a função a cada linha da coluna 'location' e criar uma nova coluna 'country'
df_liquor_dist['Dist_Pais'] = df_liquor_dist['Dist_Localizacao'].apply(lambda loc: get_country_geocode_xyz(loc))

# Exibir o DataFrame atualizado
print(df7)

df7

df_liquor_dist.head(3)

"""##### Salvando

###### Metodo GCP
"""

'''# Escreve o DataFrame tratado em um novo arquivo CSV
output_path = "gs://datalake_vendas/dados_tratados/Liquor_Sales_Dist_Tratado.csv"
df_liquor_dist.to_csv(output_path, index=False)



# ID do projeto
id_projeto = 'seu_id_projeto'

# Nome da tabela permanente no BigQuery
nome_tabela = 'tb_distribuidoras'

# Crie um cliente BigQuery com o ID do projeto
client = bigquery.Client(project=id_projeto)

# Carregue o DataFrame Pandas para a tabela permanente no BigQuery (anexar dados)
tabela_ref = client.dataset('db_vendas').table(nome_tabela)
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Adiciona os dados à tabela existente
)
job = client.load_table_from_dataframe(df_liquor_dist, tabela_ref, job_config=job_config)
job.result()  # Aguarda a conclusão do carregamento

"""##### Metodo Colab"""

#Escreve o df para um diretorio o Colab
output_path = "/content/Bases/Liquor_Sales_Distribuidores_Tratado.csv"
df_liquor_dist.to_csv(output_path, index=False)

"""### Tratamento Clientes e Distribuidora"""

!pip install kaggle

!kaggle datasets download -d starbucks/store-locations

!kaggle datasets download -d sakshigoyal7/credit-card-customers

import zipfile
import os

pasta_raiz = '/content'  # Pasta raiz do Colab
pasta_destino = '/content'  # Pasta de destino para os arquivos descompactados
arquivos_zip = ['credit-card-customers.zip', 'store-locations.zip']  # Lista de arquivos zip

for arquivo_zip in arquivos_zip:
  # Remova a extensão ".zip" do nome do arquivo
  nome_pasta = os.path.splitext(arquivo_zip)[0]

  # Crie o caminho para a pasta descompactada
  pasta_descompactada = os.path.join(pasta_destino, nome_pasta)

  # Verifique se a pasta existe. Se não, crie-a.
  if not os.path.exists(pasta_descompactada):
    os.makedirs(pasta_descompactada)

  # Descompacte o arquivo zip na pasta especificada
  with zipfile.ZipFile(os.path.join(pasta_raiz, arquivo_zip)) as zip_ref:
    zip_ref.extractall(pasta_descompactada)

# Importando a base dos códigos

import pandas as pd

locations = pd.read_csv('/content/store-locations/directory.csv')
customers = pd.read_csv('/content/credit-card-customers/BankChurners.csv')

"""#### Distribuidores"""

locations.head(1)

!pip install pycountry

import pandas as pd
import pycountry

# Carregar os dados
# Mapear as siglas dos países para os nomes completos usando a biblioteca pycountry
def get_country_name(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except AttributeError:
        return "Country not found"

# Aplicar a função para obter o nome completo do país para cada sigla na coluna 'Country Code'
locations['Pais'] = locations['Country'].apply(get_country_name)

locations.head(5)

locations = locations.reindex(columns=['Store Number', 'Store Name', 'Ownership Type', 'Street Address', 'City', 'State/Province', 'Pais', 'Postcode',
       'Phone Number', 'Longitude', 'Latitude'])

locations.rename(columns={'Store Number': 'Dist_Cod', 'Store Name':'Dist_Nome', 'Ownership Type':'Dist_Tipo', 'Street Address':'Dist_Endereco', 'City':'Dist_Cidade',
                          'State/Province':'Dist_Estado', 'Pais':'Dist_Pais', 'Postcode':'Dist_Codigo_postal', 'Phone Number':'Dist_Telefone', 'Longitude':'Dist_Longitude', 'Latitude':'Dist_Latitude'}, inplace=True)

"""Final"""

locations.head(10)

output_path = "/content/Bases/Distribuidores.csv"
locations.to_csv(output_path, index=False)

"""#### Clientes"""

customers.head(3)

customers.columns

customers = customers.reindex(columns=['CLIENTNUM', 'Attrition_Flag', 'Customer_Age', 'Gender','Dependent_count', 'Education_Level', 'Marital_Status','Card_Category'])
customers.rename(columns={'CLIENTNUM':'Cliente_Cod', 'Attrition_Flag': 'Cliente_Status', 'Customer_Age':'Cliente_Idade', 'Gender':'Cliente_Genero', 'Education_Level':'Cliente_Nivel_Educacao', 'Marital_Status':'Estado_Civil', 'Card_Category': 'Categoria_Cartao'}, inplace=True)
customers.head(1)

output_path = "/content/Bases/Clientes.csv"
locations.to_csv(output_path, index=False)

"""### Random API

#### Carregando
"""

randomapi = pd.read_csv('/content/Bases/dados_tratados_dados_random_tratados.csv')
randomapi.head(1)

"""#### Tratamento"""

randomapi_tratado = randomapi.drop('Pais', axis=1)

"""Colocando Fatura_total"""

randomapi_tratado['Fatura_Total'] = randomapi_tratado['Quantidade'] * randomapi_tratado['Preco_Unitario']
randomapi_tratado['Fatura_Total'] = randomapi_tratado['Fatura_Total'].round(2)

"""Arrumando ordem Data"""

randomapi_tratado['Data'] = pd.to_datetime(randomapi_tratado['Data'])
randomapi_tratado['Data'] = randomapi_tratado['Data'].dt.strftime('%d/%m/%Y %H:%M')

"""Colocando na ordem"""

nova_ordem = ['Cod_Fatura', 'Produto', 'Quantidade','Preco_Unitario','Fatura_Total','Data']
randomapi_tratado = randomapi_tratado[nova_ordem]

"""Final"""

randomapi_tratado.head(1)

"""Salvando"""

randomapi_tratado.to_csv('/content/Bases/randomapi_tratado.csv',index=False)

"""### Colocando ids nas Faturas (E-commerce data.csv)"""

df_vendas_tratado['Cliente_Cod'] = np.random.choice(customers['Cliente_Cod'], size=len(df_vendas_tratado))
df_vendas_tratado['Dist_Cod'] = np.random.choice(locations['Dist_Cod'], size=len(df_vendas_tratado))

nova_ordem = ['Cod_Fatura', 'Produto', 'Quantidade','Preco_Unitario','Fatura_Total','Data','Cliente_Cod','Dist_Cod']

# Reordenar as colunas do DataFrame
df_vendas_tratado = df_vendas_tratado[nova_ordem]


df_vendas_tratado = df_vendas_tratado.rename(columns={'Cod_Fatura': 'Fatura_Cod'})

"""#### Final"""

df_vendas_tratado.head(5)

"""#### Salvando"""

df_vendas_tratado.to_csv('/content/Bases/data_tratado_final.csv',index=False)

from google.colab import auth
auth.authenticate_user()

"""Salando no datalake"""

# Escreve o DataFrame tratado em um novo arquivo CSV
output_path = "gs://dl_vendas/dados_tratados/data_tratado_final.csv"
df_vendas_tratado.to_csv(output_path, index=False)



# ID do projeto
id_projeto = 'ID_PROJETO_GCP'

# Nome da tabela permanente no BigQuery
nome_tabela = 'tb_vendas'

# Crie um cliente BigQuery com o ID do projeto
client = bigquery.Client(project=id_projeto)

# Carregue o DataFrame Pandas para a tabela permanente no BigQuery (anexar dados)
tabela_ref = client.dataset('db_vendas').table(nome_tabela)
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Adiciona os dados à tabela existente
)
job = client.load_table_from_dataframe(df_vendas_tratado, tabela_ref, job_config=job_config)
job.result()  # Aguarda a conclusão do carregamento

"""### Colocando Clientes nas Faturas (Licores data.csv)"""

df_liquor_ord['Cliente_Cod'] = np.random.choice(customers['Cliente_Cod'], size=len(df_liquor_ord))
df_liquor_ord['Dist_Cod'] = np.random.choice(locations['Dist_Cod'], size=len(df_liquor_ord))

nova_ordem = ['Fatura_Cod', 'Produto', 'Quantidade','Preco_Unitario','Fatura_Total','Data','Cliente_Cod','Dist_Cod']

# Reordenar as colunas do DataFrame
df_liquor_ord = df_liquor_ord[nova_ordem]

df_liquor_ord.head(1)

"""##### Salvando"""

df_liquor_ord.to_csv('/content/Bases/Liquor_Sales_Final.csv',index=False)

# Escreve o DataFrame tratado em um novo arquivo CSV
output_path = "gs://dl_vendas/dados_tratados/Liquor_Sales_Tratado.csv"
df_liquor_ord.to_csv(output_path, index=False)



# ID do projeto
id_projeto = 'galvanized-sled-425803-b5'

# Nome da tabela permanente no BigQuery
nome_tabela = 'tb_vendas'

# Crie um cliente BigQuery com o ID do projeto
client = bigquery.Client(project=id_projeto)

# Carregue o DataFrame Pandas para a tabela permanente no BigQuery (anexar dados)
tabela_ref = client.dataset('db_vendas').table(nome_tabela)
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Adiciona os dados à tabela existente
)
job = client.load_table_from_dataframe(df_liquor_ord, tabela_ref, job_config=job_config)
job.result()  # Aguarda a conclusão do carregamento

"""Colocando IDS na random API"""

randomapi_tratado['Cliente_Cod'] = np.random.choice(customers['Cliente_Cod'], size=len(randomapi_tratado))
randomapi_tratado['Dist_Cod'] = np.random.choice(locations['Dist_Cod'], size=len(randomapi_tratado))

nova_ordem = ['Cod_Fatura', 'Produto', 'Quantidade','Preco_Unitario','Fatura_Total','Data','Cliente_Cod','Dist_Cod']

# Reordenar as colunas do DataFrame
randomapi_tratado = df_vendas_tratado[nova_ordem]

randomapi_tratado['Fatura_Cod'] = randomapi_tratado['Fatura_Cod'].astype(str)

randomapi_tratado['Data'] = pd.to_datetime(randomapi_tratado['Data'])

randomapi_tratado['Data'] = randomapi_tratado['Data'].dt.strftime('%d/%m/%Y %H:%M')

randomapi_tratado.head(5)

randomapi_tratado.to_csv('/content/Bases/randomapi_tratado_final.csv',index=False)

# Escreve o DataFrame tratado em um novo arquivo CSV
output_path = "gs://dl_vendas/dados_tratados/randomapi_tratado.csv"
randomapi_tratado.to_csv(output_path, index=False)



# ID do projeto
id_projeto = 'ID_PROJETO_GCP'

# Nome da tabela permanente no BigQuery
nome_tabela = 'tb_vendas'

# Crie um cliente BigQuery com o ID do projeto
client = bigquery.Client(project=id_projeto)

# Carregue o DataFrame Pandas para a tabela permanente no BigQuery (anexar dados)
tabela_ref = client.dataset('db_vendas').table(nome_tabela)
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Adiciona os dados à tabela existente
)
job = client.load_table_from_dataframe(randomapi_tratado, tabela_ref, job_config=job_config)
job.result()  # Aguarda a conclusão do carregamento