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

- **Docker Compose** com dois serviços:
  - **PostgreSQL**: banco de metadados do Airflow.
  - **Airflow**: um único serviço com webserver + scheduler, usando **LocalExecutor** (sem Redis, sem workers separados).
- **Volumes** para `dags/`, `logs/` e, se necessário, `plugins/`.
- Acesso ao S3 via credenciais AWS (perfil default ou variáveis de ambiente).

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
- (A definir) Caminho exato e formato do arquivo de vendas no S3.

---

## Como rodar (após implementação)

1. Copiar `.env.example` para `.env` e ajustar (ex.: `AIRFLOW_UID`, variáveis AWS se não usar perfil default).
2. Na pasta `docker/`: `docker-compose up -d`.
3. Aguardar inicialização; interface web em **http://localhost:8080** (usuário/senha conforme configurado no Compose).
4. DAGs em `dags/` serão carregados automaticamente.

*(Comandos e variáveis exatas serão documentados quando o `docker-compose.yml` for implementado.)*

---

## Repositório

- **GitHub**: [Danielhlw/airflow-aws-orchestration](https://github.com/Danielhlw/airflow-aws-orchestration)

---

## Próximos passos (roadmap)

1. Definir caminho e formato do arquivo de vendas no S3.
2. Implementar `docker-compose.yml` (Postgres + Airflow, LocalExecutor) e `.env.example`.
3. Implementar DAG de ETL de vendas (leitura S3 → transformação → destino).
4. Modelar e criar fatos/dimensões (S3 e/ou PostgreSQL).
5. Documentar no README e, se necessário, em `docs/` (modelo de dados, convenções).
6. (Opcional) GitHub Actions para validar import e sintaxe dos DAGs.
