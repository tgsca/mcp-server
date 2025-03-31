FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Install the package in editable mode
RUN pip install -e .

EXPOSE 8000

CMD ["python", "src/main.py"]