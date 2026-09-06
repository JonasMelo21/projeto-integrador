# Diario de Bordo - Ideias Relacionadas à parte de ML do projeto

## Introdução
-   Usarie este arquivo para documentar minhas novas ideias relacionadas ao projeto, especificamente à disciplina de machine learning, como, por exemplo, quais modelos utilizar, quais ferramentas aderir e etc

## Ideias de Ferramentas
-   Algumas ferramentas que estou curioso e que deverei pesquisar para incluir no projeto, se elas solucionarem um problema recorrente no projeto.

-   Lista de ferramentas para explorar:
    -   Airflow
    -   Kubeflow
    -   MLFlow
    -   Snorkel
    -   pesquisar ferramentas para versionamento de dados e modelos
    -   DVC (Data Version Control)

## Boas Práticas na Fase de Arq/Requisitos
-   Decidir se é uma tarefa supervisionada (com labels), não supervisionada, semi supervisionada ou aprendizado por reforço
-   Decidir se é uma tarefa de regressão, classificação, etc
-   Selecionar uma métrica de performance

## Boas Práticas para Seguir/Investigar/Avaliar no Treinamento
-   Feature scaling: deixar as features com o mesmo range (normalizar as features) e pensar em que momento do pipeline de treinamento isso deve acontecer pra evitar data leakage
-   Versionamento de dados por tempo, modelo,etc
-   data lineage
-   usar log transformation quando há skewness (assimetria)
-   codificar variaveis categoricas
-   feature crossing para relações complexas entre variaveis para modelos em arvore
-   atenção a data leakage: quando dados de treino não estão presentes em teste ou produção
-   causas de data eçakage:
    -   scaling antes do split
    -   train test split aleatorio ao inves de ser por tempo
    -   preencher dados faltantes com dados de teste ao inves de treino
    -   poor handling of duplicates

## Decisões de arquitetura de ml
-   Diversos modelos serão treinados,avaliados e terão seus artefatos versionados.
-   Os modelos são: regressão linear que tenta prever o preço do imóvel,modelos de detecção de anomalias,modelos de clusterização, modelos de imagem e modelos em árvore.