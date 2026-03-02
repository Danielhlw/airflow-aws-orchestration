# Setup local – passo a passo

## 1. Pré-requisitos

- Docker e Docker Compose instalados
- Terminal na pasta do projeto

## 2. Criar o arquivo `.env`

Na pasta **docker/**:

```bash
cd docker
cp .env.example .env
```

(Opcional) Edite `.env` e altere:
- `AIRFLOW_UID` (no Linux, pode ser seu UID: `id -u`)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (credenciais do banco)
- `AIRFLOW_ADMIN_USER`, `AIRFLOW_ADMIN_PASSWORD` (login da interface web)

## 3. Criar a pasta de logs e permissões (Linux)

Na pasta **orchestration** (raiz do projeto):

```bash
mkdir -p logs
```

Para o Airflow conseguir escrever em `dags/` e `logs/` dentro do container, ajuste o dono (use o mesmo valor de `AIRFLOW_UID` do `.env`, ex.: 50000):

```bash
sudo chown -R 50000:0 dags logs
```

Se você preferir rodar com seu próprio UID, coloque no `.env` o resultado de `id -u` e use esse número no `chown` (ex.: `sudo chown -R $(id -u):0 dags logs`).

## 4. Subir os containers

Ainda na pasta **docker/**:

```bash
docker-compose up -d
```

Isso sobe, em ordem:

1. **postgres** – espera ficar healthy  
2. **airflow-init** – roda uma vez (cria tabelas e usuário admin), depois encerra  
3. **airflow-scheduler** – fica rodando (agenda e executa as tasks)  
4. **airflow-webserver** – fica rodando (interface na porta 8080)

## 5. Conferir se está tudo Up

```bash
docker-compose ps
```

Você deve ver `postgres`, `airflow-scheduler` e `airflow-webserver` com status “Up”. O `airflow-init` pode aparecer como “Exit 0” (normal).

## 6. Acessar a interface

- Abra no navegador: **http://localhost:8080**
- Login: use o usuário e a senha definidos em `AIRFLOW_ADMIN_USER` e `AIRFLOW_ADMIN_PASSWORD` no `.env` (padrão: **admin** / **admin**)

## 7. Logs (se precisar debugar)

```bash
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
```

Ctrl+C para sair.

## 8. Parar tudo

Na pasta **docker/**:

```bash
docker-compose down
```

Os dados do Postgres ficam no volume `postgres-db-volume`; na próxima `up` eles continuam lá.

---

## 9. DAG mínimo (hello world)

Para validar que o scheduler está executando tasks, use o DAG `dag_hello`.

**Copiar o DAG para a pasta `dags/`** (a pasta está com dono 50000 para o Airflow):

Na raiz do projeto (**orchestration/**):

```bash
sudo cp dag_hello.py dags/
sudo chown 50000:0 dags/dag_hello.py
```

**Na interface (http://localhost:8080):**

1. Aguarde alguns segundos para o scheduler escanear a pasta `dags/`.
2. Na lista de DAGs, localize **dag_hello**.
3. Ative o DAG (toggle à esquerda do nome).
4. Clique no botão **“Trigger DAG”** (ícone de play).
5. Abra o DAG e clique na task **say_hello** para ver os logs; deve aparecer `Hello from Airflow`.

Pronto: o Airflow está lendo DAGs e executando tasks com o LocalExecutor.
