# STAGE 1: TESTER
FROM python:3.12-slim AS tester

WORKDIR /app

# Copy requirements and source code
COPY requirements.txt requirements-dev.txt ./
COPY src ./src
COPY test ./test
COPY pytest.ini ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Run tests using pytest
RUN pytest test/ -v

# STAGE 2: RUNNER
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy only production requirements and source
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
