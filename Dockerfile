FROM node:22-slim

# Install Python 3 + pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Make python3 available as python
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Install Node dependencies
COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm install

# Copy rest of project
COPY . .

RUN cd frontend && npm run build

EXPOSE 3000 8000

CMD ["bash", "./start.sh"]
