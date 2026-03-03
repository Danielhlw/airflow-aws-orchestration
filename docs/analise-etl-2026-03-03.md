# Análise da execução do ETL de vendas (2026-03-03)

## Conferência no S3

Todos os arquivos esperados foram gerados no bucket `estudos-dan-sql`:

| Caminho | Tamanho | Descrição |
|---------|---------|-----------|
| `processed/vendas/vendas_cleaned.csv` | 272 B | CSV limpo (tipos normalizados) |
| `gold/vendas/dim_cliente.csv` | 51 B | Dimensão cliente |
| `gold/vendas/dim_produto.csv` | 94 B | Dimensão produto |
| `gold/vendas/dim_data.csv` | 56 B | Dimensão data |
| `gold/vendas/dim_estado.csv` | 36 B | Dimensão estado |
| `gold/vendas/fato_vendas.csv` | 184 B | Fato de vendas |

---

## Conteúdo verificado

### Processed (bronze → limpo)
- 4 linhas de dados + header.
- Colunas: pedido_id, cliente, produto, categoria, data_pedido, valor, quantidade, estado.
- Tipos: valor em float (3500.0, 150.0, etc.), quantidade em inteiro.

### Dimensões (distinct + surrogate key)
- **dim_cliente:** 3 clientes (Ana, João, Carlos) → ids 1, 2, 3.
- **dim_produto:** 3 produtos (Notebook/Eletronicos, Mouse/Eletronicos, Cadeira/Móveis) → ids 1, 2, 3.
- **dim_data:** 3 datas (2024-11-01, 2024-11-02, 2024-11-03) → ids 1, 2, 3.
- **dim_estado:** 3 estados (SP, RJ, MG) → ids 1, 2, 3.

### Fato
- 4 linhas (uma por pedido).
- Chaves estrangeiras corretas: id_cliente, id_produto, id_data, id_estado batem com as dimensões.
- valor_total = valor × quantidade (ex.: pedido 2: 150.0 × 2 = 300.0).

---

## Integridade do modelo estrela

| Pedido | Cliente (id→nome) | Produto (id→nome) | Data (id→data) | Estado (id→UF) | Valor total |
|--------|-------------------|-------------------|----------------|----------------|-------------|
| 1 | 1→Ana | 1→Notebook | 1→2024-11-01 | 1→SP | 3500.0 |
| 2 | 2→João | 2→Mouse | 1→2024-11-01 | 2→RJ | 300.0 |
| 3 | 1→Ana | 3→Cadeira | 2→2024-11-02 | 1→SP | 800.0 |
| 4 | 3→Carlos | 1→Notebook | 3→2024-11-03 | 3→MG | 3500.0 |

Todos os IDs da fato existem nas dimensões; não há FK quebrada.

---

## Conclusão

- Pipeline executou de ponta a ponta (extract → clean → build_dims_and_fact).
- Arquivos gerados no S3 com estrutura e conteúdo corretos.
- Modelo estrela consistente: fato referenciando dimensões sem erros.
