"""
DAG ETL de vendas: lê CSV do S3 (estudos-dan-sql/vendas/vendas.csv),
limpa, gera dimensões e fato, grava no S3 em gold/.
Agendado para rodar diariamente (@daily).
"""
import csv
import io
from datetime import datetime
from collections import OrderedDict

from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator

BUCKET = "estudos-dan-sql"
SOURCE_KEY = "vendas/vendas.csv"
GOLD_PREFIX = "gold/vendas"
PROCESSED_PREFIX = "processed/vendas"


def _extract(**context):
    """Baixa o CSV do S3 e retorna o conteúdo como string."""
    hook = S3Hook(aws_conn_id="aws_default")
    content = hook.read_key(key=SOURCE_KEY, bucket_name=BUCKET)
    return content or ""


def _clean(ti, **context):
    """Normaliza tipos e grava CSV limpo no S3 (processed)."""
    content = ti.xcom_pull(task_ids="extract")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        try:
            row["data_pedido"] = row["data_pedido"].strip()
            row["valor"] = float(row["valor"].replace(",", "."))
            row["quantidade"] = int(float(row["quantidade"]))
        except (ValueError, KeyError):
            continue
        rows.append(row)
    out = io.StringIO()
    if rows:
        w = csv.DictWriter(out, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    cleaned_csv = out.getvalue()
    hook = S3Hook(aws_conn_id="aws_default")
    hook.load_string(
        string_data=cleaned_csv,
        key=f"{PROCESSED_PREFIX}/vendas_cleaned.csv",
        bucket_name=BUCKET,
        replace=True,
    )
    return len(rows)


def _build_dims_and_fact(ti, **context):
    """Lê o CSV limpo do S3, monta dimensões e fato, grava em gold/."""
    hook = S3Hook(aws_conn_id="aws_default")
    content = hook.read_key(
        key=f"{PROCESSED_PREFIX}/vendas_cleaned.csv",
        bucket_name=BUCKET,
    )
    if not content:
        return 0
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    # Dimensões (distinct + surrogate key)
    clientes = OrderedDict()
    produtos = OrderedDict()
    datas = OrderedDict()
    estados = OrderedDict()
    for r in rows:
        c = r["cliente"].strip()
        if c and c not in clientes:
            clientes[c] = len(clientes) + 1
        p = (r["produto"].strip(), r["categoria"].strip())
        if p not in produtos:
            produtos[p] = len(produtos) + 1
        d = r["data_pedido"].strip()
        if d not in datas:
            datas[d] = len(datas) + 1
        e = r["estado"].strip()
        if e not in estados:
            estados[e] = len(estados) + 1

    def _to_csv(rows_list, fieldnames):
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_list)
        return out.getvalue()

    # dim_cliente
    dim_cliente = [
        {"id_cliente": v, "nome_cliente": k} for k, v in clientes.items()
    ]
    hook.load_string(
        string_data=_to_csv(dim_cliente, ["id_cliente", "nome_cliente"]),
        key=f"{GOLD_PREFIX}/dim_cliente.csv",
        bucket_name=BUCKET,
        replace=True,
    )
    # dim_produto
    dim_produto = [
        {"id_produto": v, "produto": k[0], "categoria": k[1]}
        for k, v in produtos.items()
    ]
    hook.load_string(
        string_data=_to_csv(dim_produto, ["id_produto", "produto", "categoria"]),
        key=f"{GOLD_PREFIX}/dim_produto.csv",
        bucket_name=BUCKET,
        replace=True,
    )
    # dim_data
    dim_data = [{"id_data": v, "data": k} for k, v in datas.items()]
    hook.load_string(
        string_data=_to_csv(dim_data, ["id_data", "data"]),
        key=f"{GOLD_PREFIX}/dim_data.csv",
        bucket_name=BUCKET,
        replace=True,
    )
    # dim_estado
    dim_estado = [{"id_estado": v, "estado": k} for k, v in estados.items()]
    hook.load_string(
        string_data=_to_csv(dim_estado, ["id_estado", "estado"]),
        key=f"{GOLD_PREFIX}/dim_estado.csv",
        bucket_name=BUCKET,
        replace=True,
    )
    # fato_vendas
    fato = []
    for r in rows:
        cliente = r["cliente"].strip()
        prod = (r["produto"].strip(), r["categoria"].strip())
        data = r["data_pedido"].strip()
        estado = r["estado"].strip()
        valor = float(r["valor"]) if isinstance(r["valor"], str) else r["valor"]
        qtd = int(float(r["quantidade"])) if isinstance(r["quantidade"], str) else r["quantidade"]
        fato.append({
            "pedido_id": r["pedido_id"],
            "id_cliente": clientes.get(cliente),
            "id_produto": produtos.get(prod),
            "id_data": datas.get(data),
            "id_estado": estados.get(estado),
            "valor": valor,
            "quantidade": qtd,
            "valor_total": valor * qtd,
        })
    hook.load_string(
        string_data=_to_csv(
            fato,
            ["pedido_id", "id_cliente", "id_produto", "id_data", "id_estado", "valor", "quantidade", "valor_total"],
        ),
        key=f"{GOLD_PREFIX}/fato_vendas.csv",
        bucket_name=BUCKET,
        replace=True,
    )
    return len(fato)


with DAG(
    dag_id="dag_etl_vendas",
    description="ETL: S3 vendas → limpeza → dimensões e fato em gold/",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "vendas", "s3"],
) as dag:
    extract = PythonOperator(
        task_id="extract",
        python_callable=_extract,
    )
    clean = PythonOperator(
        task_id="clean",
        python_callable=_clean,
    )
    build_dims_fact = PythonOperator(
        task_id="build_dims_and_fact",
        python_callable=_build_dims_and_fact,
    )

    extract >> clean >> build_dims_fact
