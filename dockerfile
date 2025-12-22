FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./tests ./tests

ENV PYTHONPATH=/app/src

RUN pytest tests -vv --maxfail=1

CMD ["python", "-m", "historyserver"]