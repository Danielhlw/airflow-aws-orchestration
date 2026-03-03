# Como confirmar que o ETL de vendas rodou no S3

Depois que o DAG **dag_etl_vendas** termina com as três tasks em **success** na UI, você pode conferir os arquivos gerados no bucket.

## 1. Listar o que foi gerado

```bash
# Processado (CSV limpo)
aws s3 ls s3://estudos-dan-sql/processed/vendas/

# Gold (dimensões e fato)
aws s3 ls s3://estudos-dan-sql/gold/vendas/
```

Você deve ver:
- `processed/vendas/vendas_cleaned.csv`
- `gold/vendas/dim_cliente.csv`
- `gold/vendas/dim_produto.csv`
- `gold/vendas/dim_data.csv`
- `gold/vendas/dim_estado.csv`
- `gold/vendas/fato_vendas.csv`

## 2. Ver o conteúdo (primeiras linhas)

```bash
# CSV limpo
aws s3 cp s3://estudos-dan-sql/processed/vendas/vendas_cleaned.csv - | head -10

# Dimensão cliente
aws s3 cp s3://estudos-dan-sql/gold/vendas/dim_cliente.csv - | head -10

# Fato
aws s3 cp s3://estudos-dan-sql/gold/vendas/fato_vendas.csv - | head -10
```

## 3. Baixar para inspecionar no PC

```bash
mkdir -p /tmp/etl-vendas
aws s3 cp s3://estudos-dan-sql/processed/vendas/ /tmp/etl-vendas/processed/ --recursive
aws s3 cp s3://estudos-dan-sql/gold/vendas/ /tmp/etl-vendas/gold/ --recursive
ls -la /tmp/etl-vendas/processed/ /tmp/etl-vendas/gold/
```

Use o perfil default da AWS (ou `--profile default` se precisar). Se usar variáveis de ambiente, exporte-as antes ou use o mesmo `.env` do projeto.
