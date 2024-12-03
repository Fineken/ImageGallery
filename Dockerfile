FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static/uploads && \
    chmod 777 static/uploads

EXPOSE 5000

CMD ["python", "app.py"] 