FROM python:3.12-slim
EXPOSE 8000
VOLUME /data
ENV PYTHONUNBUFFERED 1
RUN apt update -y && apt install -y sqlite3 rsync && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
RUN ln -s /data /app/data
RUN /usr/local/bin/pip install .
CMD ["/usr/local/bin/flask", "--app", "events", "run", "-h", "0.0.0.0", "-p", "8642"]
