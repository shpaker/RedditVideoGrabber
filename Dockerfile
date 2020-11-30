FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check --requirement requirements.txt

COPY ./rvg /rvg

ENTRYPOINT ["python", "-m", "rvg"]
