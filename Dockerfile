FROM python:3.9

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all application files
COPY . .

# Expose port (Render uses PORT env variable, default 10000)
EXPOSE 10000

# Use PORT environment variable provided by Render
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
