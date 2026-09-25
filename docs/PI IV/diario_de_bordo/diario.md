# Diario - Documentando Decisões

## 05/09 - Limpeza de Dados

Percebi que os dados estão sujos e precisarei decidir como lidar com esses dados:
**area_m2**:
 -  há um imovel com area igual a 1 (verificar se foi erro de raspagem)
 -  verificar se os imoveis com area amxima (20 000 m2) são erros de raspagem

**quartos**:
  - há apenas 609(58%) imoveis dos 1050 com qtdade de quartos cadastrados, verificar se é erro de raspagem

**suites**:
  - o numero de imoveis com a informação de suites preenchida tbm é menor, verificar o porque
  - apenas 447 dos 1050, 42% preenchido

**banheiros**:
- apenas 25 linhas com a coluna banheiros não são nulos
- 2.4 % dos imoveis com esse dado preenchido

**vagas**:
- há um imovel com 144 vagas de acordo com a tabela (verificar se foi problema de raspagem)
- apenas 57% dos imoveis tem essa coluna preenchida (600 de 1050)

**preco**:
 - a tabela acima mostra que há imoveis cujo aluguel é de 140 reais (verificar a url e ver se foi erro de raspagem)
 - 25% dos alugueis custam menos de 3300 reais
 - 50% dos alugueis custam menos de 6000 reais
 - 75% dos alugueis custa menos de 15000 reais
 - há imoveis custando 610 000 reais (investigar se não foi erro na etapa de raspagem)

## 17/09 O que pode ser feito com esses dados
- transformação log pra balancear outliers em area
- escolher um test dataset com amostras representativas das areas dos imoveis
- verificar na url dos imoveis do porque esses erros (problema do site mesmo ou da raspagem)

## 19/09 - Capituos a ler para definir o que vai ser feito
Para lidar com imóveis cuja `area_m2` é muito diferente da maioria, eu priorizaria estes capítulos:

**Designing Machine Learning Systems, Chip Huyen**

1. **Capítulo 3: Data Engineering Fundamentals**
   - Entender de onde veio o dado.
   - Verificar se o problema ocorreu na raspagem, transformação ou armazenamento.
   - Conferir formatos, unidades e valores impossíveis.

2. **Capítulo 4: Training Data**
   - Identificar amostras incorretas.
   - Entender quando um valor extremo é erro de coleta ou um caso real.
   - Avaliar como a distribuição dos dados influencia o modelo.

3. **Capítulo 5: Feature Engineering**
   - Detectar e tratar outliers.
   - Usar transformações, como `log(area_m2)`.
   - Evitar data leakage e criar variáveis mais robustas.

4. **Capítulo 6: Model Development and Offline Evaluation**
   - Comparar o desempenho do modelo com e sem os imóveis extremos.
   - Criar uma baseline.
   - Avaliar se remover ou transformar os outliers realmente melhora o modelo.

5. **Capítulo 8: Data Distribution Shifts and Monitoring**
   - Útil depois que o sistema estiver funcionando.
   - Monitorar se novos imóveis começam a apresentar áreas muito diferentes da distribuição original.

**Hands-On Machine Learning, Aurélien Géron**

1. **Capítulo 2: End-to-End Machine Learning Projects**
   - Melhor capítulo para aprender o fluxo completo: explorar, limpar, dividir os dados, preparar atributos e avaliar.

2. **Capítulo 3: Classification**
   - Menos importante para o seu problema específico, mas ajuda a entender validação e avaliação de modelos.

3. **Capítulo 4: Training Models**
   - Importante para entender como valores extremos podem afetar regressão, erro quadrático e treinamento.

4. **Capítulo 5: Decision Trees**
   - Árvores costumam ser menos sensíveis a escala e a alguns outliers. Ajuda a comparar modelos.

5. **Capítulo 6: Ensemble Learning and Random Forests**
   - Útil para testar modelos mais robustos para previsão de aluguel ou preço.

6. **Capítulo 7: Dimensionality Reduction**
   - Não é prioridade agora. Pode ajudar posteriormente na análise visual de dados multivariados.

7. **Capítulo 8: Unsupervised Learning Techniques**
   - Muito útil para encontrar imóveis anômalos ou grupos incomuns, especialmente com técnicas como clustering e detecção de anomalias.

**Ordem recomendada para o seu caso**

1. Designing ML Systems, capítulos **3, 4 e 5**.
2. Hands-On ML, capítulo **2**.
3. Hands-On ML, capítulos **4, 5 e 6**.
4. Designing ML Systems, capítulo **6**.
5. Hands-On ML, capítulo **8**, caso queira automatizar a detecção de imóveis suspeitos.
6. Designing ML Systems, capítulo **8**, para monitorar o problema em produção.

O ponto principal é: **não remova automaticamente todos os outliers**. Para cada área extrema, você deve verificar:

- A área está em `m²` ou outra unidade?
- O valor veio corretamente da fonte original?
- O imóvel realmente é um terreno, galpão, prédio ou propriedade comercial?
- O valor é impossível ou apenas raro?
- A área está coerente com quartos, banheiros, vagas e preço?
- O modelo melhora quando esse registro é removido, corrigido ou transformado?

Uma estratégia prática seria classificar os casos em:

- **Erro confirmado:** corrigir ou remover.
- **Dado desconhecido:** marcar como suspeito e excluir temporariamente do treinamento.
- **Caso real, mas raro:** manter, talvez usando transformação logarítmica ou modelo robusto.
- **Tipo de imóvel diferente:** separar por categoria antes de treinar o modelo.

Para o seu notebook, o próximo passo mais importante é investigar os imóveis com `area_m2` extrema usando `id_imovel`, `titulo`, `url`, `preco`, `quartos` e `bairro` antes de decidir o tratamento.

## 19/09 - Nova execução do pipeline e planejamento da EDA2

Foi executada uma nova coleta e as camadas Bronze, Silver e Gold foram reconstruídas. O artefato observado foi `scraping_20260919_205345.json`, com 900 registros. Apesar da expectativa inicial de uma base com mais de 1.800 imóveis, a inspeção dos arquivos gerados confirmou 900 registros em cada camada principal. Essa diferença ficou aberta para investigação na próxima EDA.

### Decisões implementadas no pipeline

- A Bronze passou a preservar `descricao_completa`, mantendo `descricao` curta para compatibilidade com a API existente.
- A Silver extrai `tipo_imovel` por Regex a partir da URL e do título, com as categorias `apartamento`, `casa`, `galpao`, `lote`, `sala` e `outro`.
- Os sanity checks não removem registros. Cada linha recebe `flag_suspeito` e `motivo_suspeita` quando viola uma regra de qualidade.
- Foram sinalizados casos como preço ausente ou não positivo, área ausente ou não positiva, área residencial menor que 10 m², área residencial maior que 2.000 m², área não residencial maior que 20.000 m², mais de 20 vagas e preço fora do intervalo de R$ 100 a R$ 200.000.
- A imputação de `quartos`, `suites` e `vagas` é determinística, usando a mediana de `bairro + tipo_imovel` e fallback para a mediana global.
- `banheiros` foi removido do contrato analítico e das features do modelo devido à cobertura muito baixa.
- A Gold calcula medianas e MADs por `bairro + tipo_imovel`, ignorando suspeitos.
- O split temporal acontece antes do cálculo estatístico: 70% para treino, 15% para validação e 15% para teste.
- Os suspeitos permanecem na Silver, Gold e nos Parquets de split, mas são removidos pelo carregador ML somente do treino.
- As estatísticas ajustadas no treino são aplicadas à validação e ao teste por `merge`, evitando data leakage.

### Artefatos gerados

- `data/silver/imoveis_limpos.parquet`: 900 registros, 41 suspeitos.
- `data/gold/fact_imoveis_gold.parquet`: 900 registros preservados para auditoria e consulta.
- `data/gold/ml_train.parquet`: 630 registros, 32 suspeitos antes do filtro ML.
- `data/gold/ml_valid.parquet`: 135 registros, 5 suspeitos.
- `data/gold/ml_test.parquet`: 135 registros, 4 suspeitos.
- `data/gold/dim_bairros_estatisticas.parquet`: estatísticas por bairro e tipo, ajustadas no treino limpo.

### Plano da EDA2

A nova EDA será descritiva e não alterará as regras do pipeline. Ela deverá:

1. Conferir o volume bruto e o volume de cada camada, incluindo duplicatas e IDs únicos.
2. Comparar os schemas Bronze, Silver e Gold.
3. Medir a cobertura de preço, área, quartos, suítes e vagas.
4. Descrever a distribuição de `tipo_imovel` e sua relação com bairro.
5. Quantificar `flag_suspeito` e decompor `motivo_suspeita`.
6. Listar amostras suspeitas com URL, título, tipo, bairro, preço e área para investigação posterior.
7. Comparar as distribuições de preço, área e preço por m² por tipo de imóvel.
8. Inspecionar as estatísticas Gold e a distribuição de `target_preco` por split.
9. Registrar perguntas abertas, especialmente a diferença entre os 900 registros observados e a expectativa de mais de 1.800.

A EDA2 ficará em `notebooks/eda2.ipynb` e servirá como retrato da carga atual. Qualquer nova regra de qualidade deverá ser decidida no código do pipeline e documentada separadamente.