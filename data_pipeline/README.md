# Data Pipeline

Este módulo coordena o fluxo de dados do projeto, desde a coleta no site de anúncios até a preparação para modelagem em machine learning.

A arquitetura atual segue a lógica de camadas:

- Bronze: dados brutos extraídos do site
- Silver: dados limpos, padronizados e prontamente consumíveis
- Gold: dados model-ready, com dimensões e tabela fato para downstream analítico e ML

O fluxo principal é:

1. [data_pipeline/scraper/scraper_to_bronze.py](scraper/scraper_to_bronze.py) coleta dados de imóveis
2. [data_pipeline/medallion/bronze_to_silver.py](medallion/bronze_to_silver.py) limpa e normaliza os dados
3. [data_pipeline/medallion/silver_to_gold.py](medallion/silver_to_gold.py) cria as dimensões e a tabela fato Gold

---

## 1. Fluxo dos dados

O pipeline salva os arquivos em diretórios sob a raiz do projeto:

- data/bronze/: dados crus coletados do scraper
- data/silver/: dados limpos e padronizados em parquet
- data/gold/: dados prontos para consumo analítico/modelagem

A jornada típica é:

- scraper lê páginas do DFImoveis
- gera um JSON/CSV com imóveis em bruto
- Bronze armazena esse material bruto
- Silver aplica limpeza, deduplicação e padronização
- Gold cria as entidades de negócio e os indicadores de qualidade/feature engineering

---

## 2. O que o scraper busca

O scraper em [data_pipeline/scraper/scraper_to_bronze.py](scraper/scraper_to_bronze.py) busca imóveis de aluguel do DF.

Ele extrai as seguintes informações principais:

- id_hex: identificador único do imóvel, gerado a partir da URL
- id_imovel: identificador do imóvel presente no site
- titulo: título do anúncio
- url: URL do anúncio
- preco: valor do aluguel
- descricao: descrição do imóvel
- quartos: número de quartos
- suites: número de suítes
- vagas: número de vagas/garagens
- area: área do imóvel, normalmente em texto como "36 m²"
- bairro: bairro identificado pelo título
- imagem: primeira imagem do anúncio
- imagens: lista completa de imagens
- imobiliaria: nome da imobiliária
- data_extracao: timestamp da coleta

Além disso, o scraper tenta detectar o bairro a partir do título e usa uma lista fixa de bairros do DF como referência.

A coleta é feita com Playwright + BeautifulSoup, e cada página é navegada e processada para extrair cards de imóveis e armazenar os dados em arquivos JSON/CSV na camada Bronze.

---

## 3. Bronze para Silver

O módulo [data_pipeline/medallion/bronze_to_silver.py](medallion/bronze_to_silver.py) é responsável por transformar os dados brutos em uma camada limpa e padronizada.

### 3.1. Entrada

A Silver recebe os arquivos JSON da camada Bronze, concatena todos os registros e tenta remover duplicatas por id_hex.

### 3.2. Transformações aplicadas

As principais transformações são:

- concatenação de múltiplos arquivos Bronze
- deduplicação por id_hex usando a data mais recente
- conversão de preço para valor numérico
- extração de área em metros quadrados
- extração de números de quartos, suítes e vagas
- limpeza de texto de título e descrição
- remoção de colunas redundantes do bronze, como url, imagem, imagens e id_imovel
- criação de novas colunas úteis para análise/modelagem:
  - area_m2
  - preco_por_m2
  - titulo_len
  - descricao_len
  - ingestion_datetime
  - pipeline_version

### 3.3. Colunas que permanecem ao final da Silver

A Silver mantém as colunas essenciais do negócio, além de campos úteis para downstream analítico e modelagem. Em linhas gerais, a tabela final inclui:

- id_hex
- titulo
- descricao
- bairro
- cidade
- uf
- preco
- area_m2
- quartos
- suites
- banheiros
- vagas
- imobiliaria
- data_extracao
- source_file
- preco_por_m2
- titulo_len
- descricao_len
- ingestion_datetime
- pipeline_version

A finalidade da Silver é preservar o contexto do imóvel e normalizar os dados para que a Gold possa construir tabelas de negócio e features sem precisar reprocessar a origem bruta.

### 3.4. Saída

A Silver produz mais de um artefato parquet, não apenas o dataset principal de imóveis limpos.

Os arquivos gerados são:

- data/silver/imoveis_limpos.parquet
- data/silver/dim_imobiliarias.parquet
- data/silver/dim_bairros.parquet

O arquivo principal da Silver continua sendo `imoveis_limpos.parquet`, mas a camada também persiste as dimensões que alimentam downstream analítico e a Gold.

---

## 4. Silver para Gold

O módulo [data_pipeline/medallion/silver_to_gold.py](medallion/silver_to_gold.py) transforma a Silver em dados prontos para consumo analítico/modelagem.

A ideia aqui é separar as entidades e evitar um único dataset monolítico. O script cria modelos orientados a negócio em vez de apenas empilhar tudo em um único DataFrame.

Importante: a Silver já gera as dimensões de bairro e imobiliária; a Gold então complementa esse fluxo com agregados estatísticos e a tabela fato.

### 4.1. Dimensões criadas

#### dim_imobiliarias

Tabela de dimensão com as imobiliárias identificadas.

Colunas principais:

- id_imobiliaria
- nome_imobiliaria

#### dim_bairros

Tabela de dimensão com os bairros.

Colunas principais:

- id_bairro
- bairro
- cidade
- uf

#### dim_bairros_estatisticas

Tabela de agregados estatísticos por bairro.

Inclui medidas como:

- preco_mediano_por_m2
- preco_mad
- area_mediana_m2
- area_mad

Essas estatísticas ajudam a contextualizar o preço e a área do imóvel em relação ao bairro, mas sem misturar esse cálculo diretamente na dimensão base do bairro.

### 4.2. Tabela fato

A camada Gold gera também a tabela fato:

- fact_imoveis_gold.parquet

Ela preserva os atributos do imóvel e as features derivadas, por exemplo:

- id_imovel
- id_imobiliaria_fk
- id_bairro_fk
- titulo
- url
- bairro
- preco
- area_m2
- quartos
- suites
- banheiros
- vagas
- preco_por_m2
- imobiliaria
- imobiliaria_hash
- preco_med
- preco_mad
- area_med
- area_mad
- target_preco
- area_cat
- bairro_area_cross
- data_extracao

### 4.3. Feature engineering aplicado na Gold

Antes do split de treino/validação/teste, a Gold calcula:

- hashing da imobiliária para reduzir cardinalidade
- medianas e MAD por bairro
- target de preço (barato, justo, caro)
- categoria de área (Compacto, Padrao, Amplo)
- feature cross bairro + categoria de área

Esses campos são úteis para modelagem, mas o split train/valid/test é decidido no momento do treinamento, não nesta camada.

### 4.4. Regra importante

A Gold não salva train/valid/test em disco. Isso fica para a etapa de treinamento/modelagem, seguindo boas práticas de prevenção de leakage e separação de responsabilidades.

---

## 5. Resumo do caminho completo

O fluxo real do projeto é:

1. Site → [scraper_to_bronze.py](scraper/scraper_to_bronze.py)
2. Bronze (raw) → JSON/CSV com dados crus
3. Bronze → [bronze_to_silver.py](medallion/bronze_to_silver.py)
4. Silver (limpo e normalizado) → parquet
5. Silver → [silver_to_gold.py](medallion/silver_to_gold.py)
6. Gold (dimensões + fato + features) → parquet pronto para modelagem

---

## 6. Observações práticas

- Bronze é a camada de coleta e preservação do dado bruto.
- Silver é a camada de padronização e limpeza operacional.
- Gold é a camada de estrutura de negócio + ML-ready data.
- O split train/valid/test não deve acontecer na camada Gold; ele deve acontecer no momento de treinamento.

Esse desenho deixa o pipeline mais sustentável, previsível e alinhado a boas práticas de arquitetura de dados e engenharia de ML.
