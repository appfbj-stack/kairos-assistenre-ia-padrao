FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project root for core + aion packages
COPY pyproject.toml .
COPY core/ ./core/
COPY kairos-aion-integration/ ./kairos-aion-integration/

# Install core + aion packages
RUN pip install -e . && pip install -e ./kairos-aion-integration

COPY backend/ .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
