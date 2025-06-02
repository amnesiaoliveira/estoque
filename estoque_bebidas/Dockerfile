# Dockerfile
FROM python:3.11-slim

WORKDIR /estoque_bebida

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "estoque_bebida/manage.py"]
