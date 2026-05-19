FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 myuser
USER myuser

EXPOSE 3000

HEALTHCHECK CMD curl --fail http://localhost:3000/healthcheck || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app"]