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