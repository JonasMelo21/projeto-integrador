# Database - Schema RentMaster 🗄️

> **Entender a modelagem do banco de dados e como fazer queries**.

---

## 📐 Star Schema (Dimensional Model)

RentMaster usa **Star Schema** para consultas rápidas e BI:

```
                          FactImovel (Central)
                         /       |       \
                        /        |        \
            DimImobiliaria  DimLocal  DimTempo
                (Empresa)    (Bairro)   (Data)
```

---

## 🏢 Tabelas

### 1️⃣ DimImobiliaria (Dimensão: Empresa)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id_imobiliaria` | INT (PK) | ID único da imobiliária |
| `nome_empresa` | STRING | Nome (ex: "Imobiliária ABC") |
| `created_at` | DATETIME | Data de criação |

**Exemplos**:
```
1, "Imobiliária ABC", 2026-04-01 10:00:00
2, "Imobiliária XYZ", 2026-04-02 11:00:00
21, "Aguiar de Vasconcelos", 2026-04-15 15:00:00
```

**Queries Úteis**:
```sql
-- Top 5 imobiliárias por volume de anúncios
SELECT i.nome_empresa, COUNT(f.id_imovel) as total
FROM dim_imobiliarias i
LEFT JOIN fact_imoveis f ON i.id_imobiliaria = f.id_imobiliaria
GROUP BY i.id_imobiliaria
ORDER BY total DESC
LIMIT 5;

-- Imobiliária com maior preço médio
SELECT i.nome_empresa, AVG(f.preco) as preco_medio
FROM dim_imobiliarias i
JOIN fact_imoveis f ON i.id_imobiliaria = f.id_imobiliaria
GROUP BY i.id_imobiliaria
ORDER BY preco_medio DESC
LIMIT 1;
```

---

### 2️⃣ DimLocal (Dimensão: Localização)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id_local` | INT (PK) | ID único da localidade |
| `bairro` | STRING | Nome do bairro |
| `cidade` | STRING | Cidade |
| `uf` | STRING | Estado (ex: "DF", "SP") |
| `created_at` | DATETIME | Data de criação |

**Exemplos**:
```
1, "Asa Sul", "Brasília", "DF", 2026-04-01
2, "Lago Sul", "Brasília", "DF", 2026-04-01
3, "Copacabana", "Rio de Janeiro", "RJ", 2026-04-02
```

**Queries Úteis**:
```sql
-- Top 10 bairros mais caros
SELECT d.bairro, d.cidade, AVG(f.preco) as preco_medio
FROM dim_locais d
JOIN fact_imoveis f ON d.id_local = f.id_local
GROUP BY d.id_local
ORDER BY preco_medio DESC
LIMIT 10;

-- Imóveis em Brasília
SELECT COUNT(*) as total
FROM fact_imoveis f
JOIN dim_locais d ON f.id_local = d.id_local
WHERE d.cidade = 'Brasília';

-- Localidades por estado
SELECT uf, COUNT(DISTINCT bairro) as total_bairros
FROM dim_locais
GROUP BY uf
ORDER BY total_bairros DESC;
```

---

### 3️⃣ FactImovel (Fato Central: Imóvel)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id_imovel` | INT (PK) | ID único do imóvel |
| `id_hex` | STRING (UQ, IDX) | SHA-256 hash 12 chars (deduplicação) |
| `id_imobiliaria` | INT (FK) | Referência para DimImobiliaria |
| `id_local` | INT (FK) | Referência para DimLocal |
| `preco` | FLOAT | Preço em R$ |
| `area_m2` | FLOAT | Metragem quadrada |
| `quartos` | INT | Número de quartos |
| `banheiros` | INT | Número de banheiros |
| `vagas` | INT | Vagas de garagem |
| `data_extracao` | DATETIME | Quando foi scrapeado |
| `created_at` | DATETIME | Criação no banco |
| `updated_at` | DATETIME | Última atualização |

**Exemplos**:
```
1, "7c2bf7dac4f5", 5, 1, 2500.0, 120.0, 3, 1, 2, 2026-05-13 20:14:05, 2026-05-13 20:14:05
2, "8d3ag8ebd5g6", 1, 2, 3500.0, 150.0, 4, 2, 3, 2026-05-13 20:14:05, 2026-05-13 20:14:05
```

**Índices**:
```sql
-- Índices criados automaticamente
CREATE UNIQUE INDEX idx_id_hex ON fact_imoveis(id_hex);  -- Deduplicação
CREATE INDEX idx_id_imobiliaria ON fact_imoveis(id_imobiliaria);
CREATE INDEX idx_id_local ON fact_imoveis(id_local);
CREATE INDEX idx_preco ON fact_imoveis(preco);  -- Range queries
CREATE INDEX idx_data_extracao ON fact_imoveis(data_extracao);  -- Temporal
```

**Queries Úteis**:
```sql
-- Total de imóveis
SELECT COUNT(*) FROM fact_imoveis;  -- 240

-- Preço médio, min, max
SELECT 
  AVG(preco) as media,
  MIN(preco) as minimo,
  MAX(preco) as maximo
FROM fact_imoveis;

-- Distribuição por número de quartos
SELECT quartos, COUNT(*) as total
FROM fact_imoveis
GROUP BY quartos
ORDER BY quartos;

-- Imóveis caros por m² (top 5)
SELECT 
  id_imovel, 
  preco, 
  area_m2,
  ROUND(preco/area_m2, 2) as preco_por_m2
FROM fact_imoveis
ORDER BY preco_por_m2 DESC
LIMIT 5;

-- Imóveis adicionados hoje
SELECT COUNT(*) FROM fact_imoveis
WHERE DATE(data_extracao) = DATE('now');
```

---

## 🔗 Integridade Referencial

```sql
-- Foreign Keys (garantir dados válidos)
ALTER TABLE fact_imoveis 
ADD CONSTRAINT fk_imobiliaria 
FOREIGN KEY (id_imobiliaria) 
REFERENCES dim_imobiliarias(id_imobiliaria);

ALTER TABLE fact_imoveis 
ADD CONSTRAINT fk_local 
FOREIGN KEY (id_local) 
REFERENCES dim_locais(id_local);
```

---

## 🛠️ Operações Comuns

### Inserir Imóvel

```python
from sqlalchemy.orm import Session
from models import FactImovel, DimImobiliaria, DimLocal

def insert_imovel(db: Session, id_hex, preco, area, quartos, imobiliaria_nome, bairro, cidade):
    # 1. Encontrar ou criar imobiliária
    imob = db.query(DimImobiliaria).filter_by(nome_empresa=imobiliaria_nome).first()
    if not imob:
        imob = DimImobiliaria(nome_empresa=imobiliaria_nome)
        db.add(imob)
        db.flush()  # Gerar ID
    
    # 2. Encontrar ou criar local
    local = db.query(DimLocal).filter_by(bairro=bairro, cidade=cidade).first()
    if not local:
        local = DimLocal(bairro=bairro, cidade=cidade, uf="DF")
        db.add(local)
        db.flush()
    
    # 3. Inserir imóvel
    imovel = FactImovel(
        id_hex=id_hex,
        id_imobiliaria=imob.id_imobiliaria,
        id_local=local.id_local,
        preco=preco,
        area_m2=area,
        quartos=quartos,
        banheiros=1,
        vagas=1,
        data_extracao=datetime.utcnow()
    )
    db.add(imovel)
    db.commit()
```

### Atualizar Preço

```python
def update_preco(db: Session, id_hex: str, novo_preco: float):
    imovel = db.query(FactImovel).filter_by(id_hex=id_hex).first()
    if imovel:
        imovel.preco = novo_preco
        imovel.updated_at = datetime.utcnow()
        db.commit()
```

### Buscar por Filtros

```python
def buscar_imoveis(db: Session, min_preco=None, max_preco=None, quartos=None):
    query = db.query(FactImovel)
    
    if min_preco:
        query = query.filter(FactImovel.preco >= min_preco)
    if max_preco:
        query = query.filter(FactImovel.preco <= max_preco)
    if quartos:
        query = query.filter(FactImovel.quartos == quartos)
    
    return query.all()
```

---

## 📊 Queries Avançadas para BI/Analytics

### 1. Dashboard Geral

```sql
-- Estatísticas gerais
SELECT 
  COUNT(DISTINCT f.id_imovel) as total_imoveis,
  COUNT(DISTINCT f.id_imobiliaria) as total_imobiliarias,
  COUNT(DISTINCT f.id_local) as total_locais,
  ROUND(AVG(f.preco), 2) as preco_medio,
  ROUND(AVG(f.area_m2), 2) as area_media,
  ROUND(AVG(f.quartos), 1) as quartos_media,
  MIN(f.preco) as preco_minimo,
  MAX(f.preco) as preco_maximo
FROM fact_imoveis f;
```

### 2. Segmentação por Preço

```sql
SELECT 
  CASE 
    WHEN preco < 2000 THEN 'Econômico'
    WHEN preco < 5000 THEN 'Acessível'
    WHEN preco < 10000 THEN 'Premium'
    ELSE 'Luxo'
  END as segmento,
  COUNT(*) as total,
  ROUND(AVG(preco), 2) as preco_medio,
  ROUND(AVG(area_m2), 2) as area_media
FROM fact_imoveis
GROUP BY segmento
ORDER BY preco_medio;
```

### 3. Evolução Temporal (últimos 7 dias)

```sql
SELECT 
  DATE(data_extracao) as data,
  COUNT(*) as imoveis_adicionados,
  ROUND(AVG(preco), 2) as preco_medio
FROM fact_imoveis
WHERE data_extracao >= DATE('now', '-7 days')
GROUP BY DATE(data_extracao)
ORDER BY data DESC;
```

### 4. Matriz Bairro × Imobiliária

```sql
SELECT 
  d.bairro,
  i.nome_empresa,
  COUNT(*) as total,
  ROUND(AVG(f.preco), 2) as preco_medio
FROM fact_imoveis f
JOIN dim_locais d ON f.id_local = d.id_local
JOIN dim_imobiliarias i ON f.id_imobiliaria = i.id_imobiliaria
WHERE d.cidade = 'Brasília'
GROUP BY d.bairro, i.nome_empresa
ORDER BY total DESC
LIMIT 20;
```

---

## 🔐 Estratégia de Backup

### SQLite Local
```bash
# Backup manual
cp backend/rental.db backend/rental.db.backup

# Restaurar
cp backend/rental.db.backup backend/rental.db
```

### Azure SQL Serverless (Production)
```bash
# Backup automático configurado no Azure
# Retenção: 7 dias
# Frequência: Diária

# Restaurar via Azure Portal:
# Azure SQL → Databases → Restore
```

---

## 🚨 Troubleshooting

### Banco corrompido

```bash
# SQLite - verificar integridade
sqlite3 backend/rental.db "PRAGMA integrity_check;"

# Rebuild
sqlite3 backend/rental.db "VACUUM;"
```

### Duplicatas (mesmo id_hex)

```sql
-- Encontrar
SELECT id_hex, COUNT(*) as duplicatas
FROM fact_imoveis
GROUP BY id_hex
HAVING COUNT(*) > 1;

-- Remover (manter mais recente)
DELETE FROM fact_imoveis
WHERE id_imovel NOT IN (
  SELECT MAX(id_imovel)
  FROM fact_imoveis
  GROUP BY id_hex
);
```

---

## 📚 Próximas Leituras

- [../guides/BACKEND.md](../guides/BACKEND.md) - API FastAPI
- [../SETUP.md](../SETUP.md) - Como testar
- [../medallion/E2E_EXECUTION_GUIDE.md](../medallion/E2E_EXECUTION_GUIDE.md) - Pipeline completo

---

**Última atualização**: Sprint 2, Maio 2026
**Autor**: RentMaster Team
