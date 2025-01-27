# Projeto Integrador – 4º Semestre Big Data  

## 📊 ETL, Análises e Machine Learning com GCP  

Este projeto foi desenvolvido como parte do **Projeto Integrador do 4º semestre de Big Data**, focando em **processamento de dados na nuvem**, **ETL**, **análises** e **machine learning**.  

Utilizamos a **Google Cloud Platform (GCP)** para gerenciar um fluxo completo de dados de vendas, desde a geração até a análise avançada.  

---

## 🏗️ Arquitetura da Solução  

🔹 **Geração de Dados** – Simulação de vendas via **RandomAPI**  
🔹 **Orquestração** – **Google Cloud Scheduler** gerenciando as execuções  
🔹 **ETL com PySpark** – Transformação e limpeza no **Cloud Functions**  
🔹 **Armazenamento** – Dados brutos no **S3** e tratados no **BigQuery**  
🔹 **Análises & Machine Learning** – Insights gerados a partir do Data Warehouse  

---

## 🔧 Tecnologias Utilizadas  

📌 **Google Cloud Platform (GCP)**  
📌 **Google Cloud Scheduler** – Orquestração de tarefas  
📌 **PySpark** – Processamento de grandes volumes de dados  
📌 **Google Cloud Functions** – Execução serverless  
📌 **S3** – Storage de dados brutos  
📌 **BigQuery** – Data Warehouse para análises  
📌 **RandomAPI** – Simulação de vendas para a base  

---

## ⚡ Como Funciona  

1️⃣ O **Google Cloud Scheduler** dispara a geração de vendas fake periodicamente  
2️⃣ Os dados são coletados via **RandomAPI** e armazenados no **S3**  
3️⃣ **Cloud Functions** processa os dados usando **PySpark**  
4️⃣ Após o tratamento, os dados são carregados no **BigQuery**  
5️⃣ **Análises e previsões** são geradas com base nos dados processados  

---

## 📂 Estrutura do Projeto  
randomapi/databases │── etl-pyspark │── cloud-functions │── bigquery│── storage-s3 │── notebooks│

---

## 👨‍💻 Equipe

AUGUSTO PINHO DE FREITAS

HAMILTON ALVES DA SILVA

JUSCILENE CECILIA DOS SANTOS VARANDAS

NICOLAS YUDJI KONDO

MARCELO AUGUSTO LUVIZUTTO

---

<p align="center"> 
  <strong> Transformando dados em insights com GCP! </strong>
</p>
