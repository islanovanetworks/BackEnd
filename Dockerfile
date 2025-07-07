FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./ /app
WORKDIR /app

RUN pip install --no-cache-dir fastapi sqlalchemy uvicorn psycopg2-binary python-jose passlib[bcrypt]