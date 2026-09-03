FROM python:3.12-slim
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ARG SENTRY_RELEASE

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV SENTRY_RELEASE=${SENTRY_RELEASE}

CMD ["flask", "run"]
