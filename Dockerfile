FROM python:3.11.4-bullseye

WORKDIR /app

COPY . /app

RUN pip install poetry

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-root

CMD ["python", "main.py"]
