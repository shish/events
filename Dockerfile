# Build frontend in an isolated environment
FROM node:18 AS build
COPY frontend/package.json frontend/package-lock.json /app/
WORKDIR /app
RUN npm install
COPY frontend /app
RUN npm run build


FROM python:3.11-slim-buster
VOLUME /data
EXPOSE 8000

ENV PYTHONUNBUFFERED 1
RUN /usr/local/bin/pip install --upgrade pip setuptools wheel
COPY backend/requirements.txt /tmp/requirements.txt
RUN /usr/local/bin/pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app
COPY --from=build /app/dist /app/frontend/dist
RUN ln -s /data ./data
RUN /usr/local/bin/pytest --cov=backend --cov-fail-under=100 --cov-report=term-missing backend/__tests__/
CMD ["/usr/local/bin/gunicorn", "-w", "4", "backend.app:create_app()", "-b", "0.0.0.0:8000"]
