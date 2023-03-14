FROM python:3.8

COPY ./app /app

WORKDIR /app

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN chmod +x ./entrypoint.sh

ENTRYPOINT "/app/entrypoint.sh"
