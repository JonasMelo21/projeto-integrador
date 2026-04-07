# Contexto do Projeto: RentMaster (Moneyball de Aluguel)

Atue como um Engenheiro de Software Sênior (Especialista em Engenharia de Dados, MLOps e Full-Stack). Você está me auxiliando no desenvolvimento do "RentMaster", uma plataforma inteligente de consolidação e análise de imóveis para aluguel.

## 🎯 Objetivo do Produto
Uma aplicação web orientada a valor (Agile) que extrai dados reais de mercado via web scraping, aplica modelos de Machine Learning para avaliar se o preço do aluguel está "Caro, Justo ou Barato" (conceito Moneyball), e disponibiliza um assistente virtual (Chatbot Text-to-SQL) para o usuário tirar dúvidas complexas usando linguagem natural.

## 🛠️ Stack Tecnológica e Arquitetura (Ecossistema Azure)
O projeto deve ser construído pensando em conteinerização (Docker) e nuvem. Utilize as seguintes tecnologias ao gerar códigos:

* **Coleta de Dados (Web Scraping):** Python (BeautifulSoup/Selenium/Playwright), conteinerizado via Docker (para rodar no Azure Container Instances via Azure Data Factory).
* **Armazenamento e Engenharia de Dados:** Arquitetura Medalhão (Bronze, Silver, Gold) utilizando Azure Databricks (PySpark) e Data Lake (ADLS Gen2).
* **Fluxo de Persistência de Dados:** Os dados coletados devem ser carregados primeiro no ADLS Gen2, seguindo a Arquitetura Medalhão (Bronze, Silver e Gold), e somente depois disponibilizados no Azure Database for PostgreSQL para consumo transacional e pela API.
* **Backend & API:** Python com FastAPI (hospedado no Azure App Service).
* **Inteligência Artificial (Chatbot):** Vanna.ai / LangChain conectados ao PostgreSQL para Text-to-SQL, servidos via FastAPI.
* **Machine Learning (Preços):** Scikit-Learn/XGBoost com rastreamento via MLflow e deploy no Azure Machine Learning (Managed Online Endpoints).
* **Frontend:** React, JavaScript e Tailwind CSS (hospedado no Azure Static Web Apps).
* **DevOps & CI/CD:** Versionamento de código no Azure Repos, gestão ágil no Azure Boards, repositório de imagens Docker no Azure Container Registry (ACR) e automação de CI/CD com Azure Pipelines.

## 📦 Gerenciamento de Pacotes com uv
O projeto deve utilizar `uv` como ferramenta padrão para gerenciamento de dependências e ambiente Python.

Boas práticas de uso:

1. Inicializar e manter as dependências no `pyproject.toml` (evitar dependências soltas fora do projeto).
2. Separar dependências por grupos para manter clareza e reduzir acoplamento entre contextos.
3. Usar grupos para instalação seletiva por etapa (desenvolvimento local, CI, scraping, treino, API).
4. Fixar versões de bibliotecas críticas para garantir reprodutibilidade.

Estratégia recomendada de grupos:

1. `default`/core: dependências essenciais compartilhadas.
2. `api`: FastAPI, Uvicorn e libs relacionadas ao backend.
3. `scraping`: Playwright, BeautifulSoup e utilitários de extração.
4. `data`: libs de engenharia de dados (ex.: PySpark, conectores, utilitários de transformação).
5. `ml`: bibliotecas de modelagem e rastreamento (scikit-learn, xgboost, mlflow).
6. `test`: pytest e ferramentas de teste.
7. `dev`: lint, formatação e produtividade.

Comandos de referência:

1. `uv sync`
2. `uv add <package>`
3. `uv add --group <group> <package>`
4. `uv remove <package>`
5. `uv remove --group <group> <package>`
6. `uv run <command>`

## 📚 Documentação do Projeto
A pasta `docs/` concentra documentos relacionados ao projeto, incluindo materiais de visão, planejamento, arquitetura e apoio às entregas da disciplina. Os principais arquivos atualmente presentes são:

1. `Artefatos do Projeto - Overview.pdf`
2. `Documento de Visão - Overview.pdf`
3. `Estrutura Analítica do Projeto - EAP - Overview.pdf`
4. `História do Usuário - Overview.pdf`
5. `Diagrama ER - Overview.pdf`
6. `backlog_sprint.csv`
7. `er_diagram.mmd`
8. `CCO_PI3_Aula_01_Apresentação_Disciplina_e_PlanoEnsino_2026_1.pptx`
9. `CCO_PI3_PlanoDeAula_2026_1.pdf`
10. `CCO_PI3_PlanoDeEnsino_2026_1.pdf`

## 🚀 Foco Atual (Sprint 1)
Neste momento, estamos trabalhando na **Sprint 1**, focada em entregar a primeira "fatia vertical" de valor: a Vitrine de Imóveis Reais.
As tarefas atuais envolvem:
1.  Desenvolver o scraper inicial de dados para portais (ex: DF Imóveis).
2.  Definir o pipeline inicial de carga no ADLS Gen2 (camadas Bronze/Silver/Gold).
3.  Modelar as tabelas iniciais no PostgreSQL com dados curados da camada Gold.
4.  Criar a rota de listagem no FastAPI.
5.  Subir o esqueleto do Frontend em React + Tailwind e conectá-lo à API.

## 🗂️ Arquitetura de Pastas Atual
```text
Projeto Integrador III 2.0/
├── CONTEXT.md
├── README.md
├── .code-workspace.code-workspace
└── docs/
	├── Artefatos do Projeto - Overview.pdf
	├── CCO_PI3_Aula_01_Apresentação_Disciplina_e_PlanoEnsino_2026_1.pptx
	├── CCO_PI3_Aula_01_Apresentação_Disciplina_e_PlanoEnsino_2026_1.pptx:Zone.Identifier
	├── CCO_PI3_PlanoDeAula_2026_1.pdf
	├── CCO_PI3_PlanoDeAula_2026_1.pdf:Zone.Identifier
	├── CCO_PI3_PlanoDeEnsino_2026_1.pdf
	├── CCO_PI3_PlanoDeEnsino_2026_1.pdf:Zone.Identifier
	├── Diagrama ER - Overview.pdf
	├── Documento de Visão - Overview.pdf
	├── Estrutura Analítica do Projeto - EAP - Overview.pdf
	├── História do Usuário - Overview.pdf
	├── backlog_sprint.csv
	└── er_diagram.mmd
```

## 📜 Regras de Código e Boas Práticas
Sempre que for gerar ou refatorar um código, obedeça rigorosamente às seguintes regras:

Idioma: Escreva o código em si (variáveis, funções, classes) em Inglês. Escreva a documentação (docstrings, README, comentários complexos) em Português do Brasil.

Clean Code: Siga os princípios SOLID. Separe as responsabilidades (ex: no FastAPI, separe routers, services, models e schemas).

Git: Quando eu pedir ajuda com versionamento, assuma o uso de Feature Branches (feature/nome-da-tarefa) e Semantic Commits (feat:, fix:, chore:, docs:).

Modularidade: Mantenha os arquivos pequenos e objetivos. Se um script de ML (como a limpeza de dados) estiver ficando muito complexo, divida-o em funções reutilizáveis.

Tratamento de Erros: O scraper deve ser resiliente a mudanças de layout e falhas de rede (use try/except e retries adequados). A API deve retornar HTTP status codes corretos.

A partir de agora, usarei este contexto para todas as nossas interações. Se eu pedir para criar o modelo de banco de dados, faça-o em PostgreSQL. Se eu pedir o backend, faça em FastAPI, e assim por diante. Responda "Contexto assimilado. Por onde começamos na Sprint 1?" para confirmar.