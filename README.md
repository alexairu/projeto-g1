# 🦟 Projeto G1: Análise e Visualização de Dados Epidemiológicos da Dengue no Brasil

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

Este repositório contém a solução completa do **Projeto G1** para a disciplina de **Linguagens de Programação**. O projeto realiza o processamento ETL (Extract, Transform, Load), persistência em banco de dados relacional SQLite, análise exploratória em Jupyter Notebook e a publicação de um **Dashboard Interativo em Streamlit**.

---

## 🔗 Links de Publicação do Projeto

- 🚀 **Streamlit Community Cloud (App Interativo):** [https://streamlit.io/](https://streamlit.io/) *(Link de demonstração)*
- 🌐 **GitHub Pages (Landing Page): https://github.com/alexairu/projeto-g1
- 📁 **Repositório GitHub:** [https://github.com/alexandrelouzada/projeto-g1](https://github.com/alexandrelouzada/projeto-g1)

---

## 📌 Visão Geral do Projeto

A dengue representa um desafio constante para a saúde pública brasileira. Este projeto analisa um histórico de **4.440 registros epidemiológicos e climáticos (2015 a 2024)** abrangendo 37 municípios de 20 Unidades Federativas.

### Objetivos Alcançados:
1. **Engenharia de Dados (ETL):** Carga do dataset CSV, cálculo de colunas derivadas (`taxa_internacao_pct` e `taxa_letalidade_pct`) e ingestão no banco SQLite (`database/dengue_brasil.db`) via SQLAlchemy.
2. **Exploração em Notebook:** Criação do notebook `notebooks/analise_dengue.ipynb` com análise de sazonalidade, cálculo de KPIs consolidados e matriz de correlação estatística de Pearson entre pluviosidade, temperatura e hospitalizações.
3. **Dashboard Web Interativo:** Aplicação desenvolvida em **Streamlit** (`app.py`) com suporte a filtros reativos em tempo real, visualizações interativas em Plotly Express e exportação de relatórios.

---

## 📂 Árvore de Diretórios do Repositório

```text
projeto-g1/
├── app.py                      # Aplicação web interativa em Streamlit
├── requirements.txt            # Lista de dependências Python do projeto
├── README.md                   # Documentação completa e instruções
├── index.html                  # Landing Page estática para o GitHub Pages
├── dados/                      # Diretório de dados brutos
│   └── simulacao_dengue_brasil.csv
├── database/                   # Banco de dados relacional SQLite
│   └── dengue_brasil.db
├── notebooks/                  # Notebooks Jupyter para análise exploratória
│   └── analise_dengue.ipynb
└── imagens/                    # Figuras e gráficos estáticos exportados
    ├── casos_acumulados_mes.png
    └── correlacao_clima_notificacoes.png
```

---

## 💻 Instruções para Execução Local

Siga o passo a passo abaixo para clonar o repositório, configurar o ambiente virtual Python e executar o aplicativo localmente:

### 1. Clonar o Repositório
```bash
git clone https://github.com/alexandrelouzada/projeto-g1.git
cd projeto-g1
```

### 2. Criar e Ativar o Ambiente Virtual (`venv`)
- **No Linux/macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **No Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  \.venv\Scripts\Activate.ps1
  ```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 4. Ingerir Dados no Banco SQLite (Opcional)
Caso deseje reprocessar a carga de dados no banco SQLite:
```bash
python -c "
import pandas as pd, numpy as np, sqlalchemy as sa
df = pd.read_csv('dados/simulacao_dengue_brasil.csv', encoding='utf-8-sig')
df['taxa_internacao_pct'] = np.where(df['casos_dengue'] > 0, (df['internacoes'] / df['casos_dengue']) * 100, 0.0)
df['taxa_letalidade_pct'] = np.where(df['casos_dengue'] > 0, (df['obitos'] / df['casos_dengue']) * 100, 0.0)
engine = sa.create_engine('sqlite:///database/dengue_brasil.db')
df.to_sql('dengue', engine, if_exists='replace', index=False)
print('Ingestão concluída!')
"
```

### 5. Executar o Dashboard no Streamlit
```bash
streamlit run app.py
```
O dashboard estará acessível no navegador em `http://localhost:8501`.

---

## 📊 Principais Resultados Analíticos

- **Total de Casos Notificados:** 3.560.562
- **Total de Internações Hospitalares:** 178.670 (~5,02% dos casos)
- **Total de Óbitos Confirmados:** 5.314
- **Taxa de Letalidade Geral:** 0,1492%
- **Sazonalidade:** Concentração significativa dos surtos entre **Janeiro e Maio**, associada aos meses de maior temperatura e pluviosidade no território nacional.

---

## 🎓 Créditos e Identificação Acadêmica

- **Disciplina:** Linguagens de Programação
- **Professor Orientador:** Alexandre Neves Louzada
- **Aluno Desenvolvedor:** Alexandre Souza de Abreu Junior
- **Instituição / Curso:** Projeto Acadêmico G1
