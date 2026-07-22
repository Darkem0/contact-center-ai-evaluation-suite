FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .
COPY fixtures ./fixtures

EXPOSE 8000
CMD ["uvicorn", "contact_center_eval.api:app", "--host", "0.0.0.0", "--port", "8000"]
