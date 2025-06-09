# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app
RUN mkdir -p data config


# Install dependencies, including git for pip installations from repositories
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
# Copy application code
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Set timezone to ensure daily trigger is based on correct server time (optional)
ENV TZ=America/Chicago

# Run the main script
CMD ["python", "main.py"]