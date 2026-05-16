FROM python:3.11-slim
WORKDIR /app
COPY app.py .
RUN pip install flask prometheus-flask-exporter
RUN mkdir -p /app/data
EXPOSE 5000
CMD ["python", "app.py"]
