# Airflow AWS Orchestration

Projeto de **estudos e testes** de orquestração com Apache Airflow, focado em ETL a partir de dados no S3 (bucket `estudos-dan-sql`), com modelo de dados em estrela (fatos e dimensões). Ambiente **local**, sem uso de EC2.

---

## Objetivo

- Usar o bucket S3 **estudos-dan-sql** (conta AWS default) como base.
- Ler um **arquivo de vendas** (ex.: CSV) do S3.
- Executar um **ETL** (extração, limpeza, transformação).
- Gerar **fatos e dimensões** (modelo estrela simples) a partir dos dados de vendas.
- Servir como base de estudos para Airflow + AWS (S3) + modelagem analítica.

---

## Como o projeto será implementado

### Arquitetura (simplificada, local)

- **Docker Compose** com três serviços: **PostgreSQL** (metadados), **airflow-scheduler** e **airflow-webserver**, usando **LocalExecutor** (sem Redis, sem workers separados).
- **Volumes** para `dags/`, `logs/`; credenciais via `.env` (incl. AWS para S3).
- Ver passo a passo em **[docs/setup.md](docs/setup.md)**.

### Fluxo de dados planejado

1. **Origem**: arquivo de vendas no S3 (ex.: `estudos-dan-sql/vendas/vendas.csv`).
2. **ETL (DAG)**:
   - Extração: leitura do arquivo no S3.
   - Limpeza/transformação: normalização, tipos, tratamento de nulos.
   - Carga: gravação do resultado em:
     - **Opção A**: mesmo S3, em outro prefixo (ex.: `processed/` ou `gold/`).
     - **Opção B**: tabelas no PostgreSQL local (fatos e dimensões).
     - **Opção C**: ambos (S3 + PostgreSQL).
3. **Modelo de dados (alvo)**:
   - **Fato**: uma linha por venda (ou por item de venda), com chaves para dimensões.
   - **Dimensões**: ex. `dim_produto`, `dim_cliente`, `dim_data`, `dim_loja` (conforme colunas do arquivo de vendas).

### Estrutura do repositório

```
airflow-aws-orchestration/
├── docker/
│   ├── docker-compose.yml    # Postgres + Airflow (LocalExecutor)
│   └── .env.example          # AIRFLOW_UID, AWS (se necessário)
├── dags/
│   └── dag_etl_vendas.py     # DAG principal: S3 → ETL → destino
├── plugins/                  # (opcional) Hooks/operators customizados
├── docs/                     # (opcional) Modelo de dados, decisões
├── .env.example
├── .gitignore
└── README.md
```

### Escopo deliberadamente fora do escopo (por ser ambiente de estudos)

- Sem Redis, CeleryExecutor ou múltiplos workers.
- Sem ambientes de staging/produção nem deploy em EC2.
- CI/CD completo opcional; possível apenas validação de DAGs no GitHub Actions.

---

## Pré-requisitos

- Docker e Docker Compose.
- Acesso AWS ao bucket `estudos-dan-sql` (perfil default em `~/.aws/credentials` ou variáveis de ambiente).
- Arquivo de vendas: **`s3://estudos-dan-sql/vendas/vendas.csv`** (CSV com pedido_id, cliente, produto, categoria, data_pedido, valor, quantidade, estado).

---

## Como rodar

Siga **[docs/setup.md](docs/setup.md)** (criar `.env`, permissões, `docker-compose up`, DAG hello e ETL). Em resumo:

1. `docker/.env` a partir de `docker/.env.example` (e variáveis AWS se necessário).
2. `docker-compose up -d` na pasta `docker/`.
3. Interface em **http://localhost:8080**; DAG **dag_etl_vendas** lê o CSV do S3, limpa e gera dimensões + fato em `s3://estudos-dan-sql/processed/` e `gold/vendas/`.

**Conferir resultado no S3:** [docs/verificar-etl-s3.md](docs/verificar-etl-s3.md).  
**Análise de uma execução:** [docs/analise-etl-2026-03-03.md](docs/analise-etl-2026-03-03.md).

---

## Repositório

- **GitHub**: [Danielhlw/airflow-aws-orchestration](https://github.com/Danielhlw/airflow-aws-orchestration)

---

## Status e próximos passos

- **Feito:** Docker (Postgres + scheduler + webserver), DAG hello, DAG ETL vendas (S3 → processed + gold), documentação em `docs/`.
- **Próximos (opcional):** GitHub Actions para validar DAGs; gravar fatos/dimensões também em PostgreSQL; agendar o ETL (ex.: `@daily`).
