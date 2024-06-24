# Use the specified JDK version
FROM python:3.10-slim as base

# Define environment variables
ENV KAFKA_VERSION=3.7.0
ENV KAFKA_SCALA_VERSION=2.13

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends wget openjdk-17-jdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and extract Kafka
RUN wget -q https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz -O /tmp/kafka.tgz && \
    mkdir -p /opt/kafka && \
    tar -xzf /tmp/kafka.tgz -C /opt/kafka --strip-components=1 && \
    rm /tmp/kafka.tgz

# Verify the config directory exists and add the advertised.listeners configuration
RUN mkdir -p /opt/kafka/config && \
    echo "advertised.listeners=PLAINTEXT://localhost:9092" >> /opt/kafka/config/server.properties

# Set environment variables for Python
ENV PATH="/opt/kafka/bin:${PATH}"
ENV KAFKA_HEAP_OPTS="-Xmx1G -Xms1G"

# Expose Kafka ports
EXPOSE 9092

# Set the entrypoint for the container
ENTRYPOINT ["/opt/kafka/bin/kafka-server-start.sh", "/opt/kafka/config/server.properties"]
