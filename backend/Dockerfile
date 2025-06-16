FROM python:3.9-bullseye

WORKDIR /api

# Install required tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    apt-transport-https \
    gnupg \
    postgresql-client \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Add Adoptium GPG key
RUN wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public \
    | gpg --dearmor \
    | tee /etc/apt/trusted.gpg.d/adoptium.gpg > /dev/null

# Add Adoptium repo for Temurin 17 (bullseye)
RUN echo "deb https://packages.adoptium.net/artifactory/deb bullseye main" \
    | tee /etc/apt/sources.list.d/adoptium.list

# Install Temurin 17 JDK
RUN apt-get update && apt-get install -y --no-install-recommends \
    temurin-17-jdk \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Environment variables
ENV JAVA_HOME=/usr/lib/jvm/temurin-17-jdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin
ENV PYTHONPATH=/app
ENV PYSPARK_PYTHON=/usr/local/bin/python
ENV PYSPARK_DRIVER_PYTHON=/usr/local/bin/python
ENV PYSPARK_SUBMIT_ARGS="--driver-memory 2g pyspark-shell"
ENV SPARK_HOME=/usr/local/lib/python3.9/site-packages/pyspark
ENV PATH=$PATH:$SPARK_HOME/bin

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Make scripts executable
RUN chmod +x start.sh wait-for-it.sh

CMD ["sh", "start.sh"]